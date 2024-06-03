import math
from lionagi.libs import CallDecorator as cd


class KnowledgeBase:
    def __init__(self):
        self.entities = {}
        self.relations = []
        self.sources = {}

    def merge_with_kb(self, kb2):
        for r in kb2.relations:
            article_url = list(r["meta"].keys())[0]
            source_data = kb2.sources[article_url]
            self.add_relation(
                r, source_data["article_title"], source_data["article_publish_date"]
            )

    def are_relations_equal(self, r1, r2):
        return all(r1[attr] == r2[attr] for attr in ["head", "type", "tail"])

    def exists_relation(self, r1):
        return any(self.are_relations_equal(r1, r2) for r2 in self.relations)

    def merge_relations(self, r2):
        r1 = [r for r in self.relations if self.are_relations_equal(r2, r)][0]
        article_url = list(r2["meta"].keys())[0]
        if article_url not in r1["meta"]:
            r1["meta"][article_url] = r2["meta"][article_url]
        else:
            spans_to_add = [
                span
                for span in r2["meta"][article_url]["spans"]
                if span not in r1["meta"][article_url]["spans"]
            ]
            r1["meta"][article_url]["spans"] += spans_to_add

    def add_entity(self, e):
        self.entities[e["title"]] = {k: v for k, v in e.items() if k != "title"}

    def add_relation(self, r, article_title, article_publish_date):
        candidate_entities = [r["head"], r["tail"]]
        entities = [self.get_entity_data(ent) for ent in candidate_entities]

        if any(ent is None for ent in entities):
            return

        for e in entities:
            self.add_entity(e)

        r["head"] = entities[0]["title"]
        r["tail"] = entities[1]["title"]

        article_url = list(r["meta"].keys())[0]
        if article_url not in self.sources:
            self.sources[article_url] = {
                "article_title": article_title,
                "article_publish_date": article_publish_date,
            }

        if not self.exists_relation(r):
            self.relations.append(r)
        else:
            self.merge_relations(r)

    def print(self):
        print("Entities:")
        for e in self.entities.items():
            print(f"  {e}")
        print("Relations:")
        for r in self.relations:
            print(f"  {r}")
        print("Sources:")
        for s in self.sources.items():
            print(f"  {s}")

    @staticmethod
    def extract_relations_from_model_output(text):
        relations = []
        # process text to extract relations
        return relations


class KGTripletExtractor:
    @staticmethod
    def text_to_kb(
        text,
        imodel,
        device="cpu",
        span_length=512,
        article_title=None,
        article_publish_date=None,
        verbose=False,
    ):
        if not imodel.is_initialized():
            imodel.initialize()

        inputs = imodel.tokenize([text], return_tensors="pt")
        num_tokens = len(inputs["input_ids"][0])
        num_spans = math.ceil(num_tokens / span_length)
        overlap = math.ceil(
            (num_spans * span_length - num_tokens) / max(num_spans - 1, 1)
        )
        spans_boundaries = []
        start = 0
        for i in range(num_spans):
            spans_boundaries.append(
                [start + span_length * i, start + span_length * (i + 1)]
            )
            start -= overlap

        tensor_ids = [
            inputs["input_ids"][0][boundary[0] : boundary[1]]
            for boundary in spans_boundaries
        ]
        tensor_masks = [
            inputs["attention_mask"][0][boundary[0] : boundary[1]]
            for boundary in spans_boundaries
        ]

        inputs = {
            "input_ids": torch.stack(tensor_ids).to(device),
            "attention_mask": torch.stack(tensor_masks).to(device),
        }

        gen_kwargs = {
            "max_length": 512,
            "length_penalty": 0,
            "num_beams": 3,
            "num_return_sequences": 3,
        }
        generated_tokens = imodel.generate(
            **inputs,
            **gen_kwargs,
        )

        decoded_preds = imodel.decode(generated_tokens)

        kb = KnowledgeBase()
        i = 0
        for sentence_pred in decoded_preds:
            current_span_index = i // 3
            relations = KnowledgeBase.extract_relations_from_model_output(sentence_pred)
            for relation in relations:
                relation["meta"] = {
                    "article_url": {"spans": [spans_boundaries[current_span_index]]}
                }
                kb.add_relation(relation, article_title, article_publish_date)
            i += 1
        return kb


class KGraph:
    @staticmethod
    def text_to_kb(text, **kwargs):
        return KGTripletExtractor.text_to_kb(text, **kwargs)

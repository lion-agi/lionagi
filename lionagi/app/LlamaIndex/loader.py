import json
from lionagi.os.libs import to_dict, to_list
from lionagi.os.primitives import Node, note, pile


def load_llamaindex_vector_store(folder):
    files = ["default__vector_store", "docstore", "index_store"]
    paths = [f"{folder}/{file}.json" for file in files]

    notes = {}
    for idx, p in enumerate(paths):
        a = json.load(open(p))
        notes[files[idx]] = note(**a)

    doc_note = notes["docstore"]
    vec_note = notes["default__vector_store"]
    index_note = notes["index_store"]

    for i in index_note["index_store/data"].keys():
        cp = ["index_store/data", i, "__data__"]
        index_note[*cp] = to_dict(index_note[*cp])

    def _get_pile_by_index(index_id_):
        cp = ["index_store/data", index_id_, "__data__", "nodes_dict"]
        try:
            index_note[*cp] = to_dict(index_note[*cp])
        except:
            raise Exception(f"Index {index_id_} not found")

        nodes_dict = index_note[*cp]
        all_nodes = list(nodes_dict.keys())
        p_ = pile()

        for i in all_nodes:
            cp = ["docstore/data", i, "__data__"]
            doc_note[*cp] = to_dict(doc_note[*cp])
            node = Node.from_obj(doc_note[*cp])

            cp = ["embedding_dict", node.metadata["id_"]]
            node.embedding = vec_note[*cp]

            p_.include(node)
        return p_

    results = [_get_pile_by_index(i) for i in index_note["index_store/data"].keys()]

    return results if len(results) > 1 else results[0]

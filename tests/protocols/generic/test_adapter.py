import pytest

from lionagi.protocols._adapter import (
    DEFAULT_ADAPTERS,
    Adapter,
    AdapterRegistry,
    CSVFileAdapter,
    ExcelFileAdapter,
    JsonAdapter,
    JsonFileAdapter,
    PandasDataFrameAdapter,
    PandasSeriesAdapter,
)


class TestAdapter:

    def test_adapter_protocol(self):
        # Verify Adapter is a Protocol
        assert isinstance(Adapter, type)
        assert hasattr(Adapter, "__protocol_attrs__")

        # Test protocol attributes
        assert "from_obj" in Adapter.__protocol_attrs__
        assert "to_obj" in Adapter.__protocol_attrs__
        assert "obj_key" in Adapter.__protocol_attrs__

        # Test protocol implementation
        class TestAdapter(Adapter):
            obj_key = "test"

            @classmethod
            def from_obj(cls, subj_cls, obj, *, many=False, **kwargs):
                return {}

            @classmethod
            def to_obj(cls, subj, *, many=False, **kwargs):
                return {}

        assert isinstance(TestAdapter(), Adapter)

    def test_adapter_registry(self):
        registry = AdapterRegistry()

        # Test registration
        registry.register(JsonAdapter)
        assert "json" in registry._adapters

        # Test getting adapter
        adapter = registry.get("json")
        assert isinstance(adapter, JsonAdapter)

        # Test list adapters
        adapters = registry.list_adapters()
        assert len(adapters) > 0

    def test_default_adapters(self):
        assert len(DEFAULT_ADAPTERS) == 6
        assert JsonAdapter in DEFAULT_ADAPTERS
        assert JsonFileAdapter in DEFAULT_ADAPTERS
        assert PandasSeriesAdapter in DEFAULT_ADAPTERS
        assert PandasDataFrameAdapter in DEFAULT_ADAPTERS
        assert CSVFileAdapter in DEFAULT_ADAPTERS
        assert ExcelFileAdapter in DEFAULT_ADAPTERS


class TestJsonAdapter:

    def test_json_adapter(self):
        adapter = JsonAdapter()

        # Test from_obj
        data = '{"key": "value"}'
        result = adapter.from_obj(str, data)
        assert result == {"key": "value"}

        # Test to_obj
        data = {"key": "value"}
        result = adapter.to_obj(data)
        assert result == '{"key":"value"}'


@pytest.fixture
def temp_json_file(tmp_path):
    file = tmp_path / "test.json"
    file.write_text('{"key": "value"}')
    return file


class TestJsonFileAdapter:

    def test_json_file_adapter(self, temp_json_file):
        adapter = JsonFileAdapter()

        # Test from_obj
        result = adapter.from_obj(str, temp_json_file)
        assert result == {"key": "value"}

        # Test to_obj
        output_file = temp_json_file.parent / "output.json"
        adapter.to_obj({"key": "value"}, fp=output_file)
        assert output_file.read_text() == '{"key": "value"}'


# Additional tests for other adapters would go here

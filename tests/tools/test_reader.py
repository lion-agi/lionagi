from pathlib import Path

import pytest

from lionagi.tools.reader.reader_tool import (
    ReaderAction,
    ReaderRequest,
    ReaderTool,
)


@pytest.fixture
def reader_tool(mock_document_converter, temp_dir):
    """Initialize ReaderTool with mocked dependencies."""
    return ReaderTool()


def test_open_document(
    reader_tool, temp_dir, sample_text, mock_file_operations
):
    """Test opening a document."""
    test_file = temp_dir / "test.txt"
    test_file.write_text(sample_text)

    request = ReaderRequest(
        action=ReaderAction.open, path_or_url=str(test_file)
    )

    response = reader_tool.handle_request(request)
    assert response.success
    assert response.doc_info is not None
    assert response.doc_info.doc_id.startswith("DOC_")
    assert response.doc_info.length is not None


def test_read_document(
    reader_tool, temp_dir, sample_text, mock_file_operations
):
    """Test reading a document with partial offsets."""
    # First open the document
    test_file = temp_dir / "test.txt"
    test_file.write_text(sample_text)

    open_request = ReaderRequest(
        action=ReaderAction.open, path_or_url=str(test_file)
    )
    open_response = reader_tool.handle_request(open_request)
    doc_id = open_response.doc_info.doc_id

    # Test reading with offsets
    read_request = ReaderRequest(
        action=ReaderAction.read, doc_id=doc_id, start_offset=5, end_offset=20
    )
    read_response = reader_tool.handle_request(read_request)

    assert read_response.success
    assert read_response.chunk is not None
    assert read_response.chunk.content is not None
    assert read_response.chunk.start_offset == 5
    assert read_response.chunk.end_offset == 20


def test_search_document(
    reader_tool, temp_dir, sample_text, mock_file_operations
):
    """Test searching within a document."""
    # First open the document
    test_file = temp_dir / "test.txt"
    test_file.write_text(sample_text)

    open_request = ReaderRequest(
        action=ReaderAction.open, path_or_url=str(test_file)
    )
    open_response = reader_tool.handle_request(open_request)
    doc_id = open_response.doc_info.doc_id

    # Test searching
    search_request = ReaderRequest(
        action=ReaderAction.search, doc_id=doc_id, search_query="test"
    )
    search_response = reader_tool.handle_request(search_request)

    assert search_response.success
    assert search_response.search_result is not None
    assert len(search_response.search_result.positions) > 0


def test_chunk_document(
    reader_tool, temp_dir, sample_text, mock_file_operations
):
    """Test document chunking functionality."""
    # First open the document
    test_file = temp_dir / "test.txt"
    test_file.write_text(sample_text)

    open_request = ReaderRequest(
        action=ReaderAction.open, path_or_url=str(test_file)
    )
    open_response = reader_tool.handle_request(open_request)
    doc_id = open_response.doc_info.doc_id

    # Test chunking
    chunk_request = ReaderRequest(
        action=ReaderAction.chunk_doc,
        doc_id=doc_id,
        chunk_size=20,
        overlap=0.1,
        threshold=5,
    )
    chunk_response = reader_tool.handle_request(chunk_request)

    assert chunk_response.success
    assert chunk_response.chunk_list is not None
    assert len(chunk_response.chunk_list) > 0

    # Verify chunk metadata
    first_chunk = chunk_response.chunk_list[0]
    assert first_chunk.index == 0
    assert first_chunk.start == 0
    assert first_chunk.end > 0
    assert first_chunk.text


def test_list_and_close_documents(
    reader_tool, temp_dir, sample_text, mock_file_operations
):
    """Test listing and closing documents."""
    # First open a document
    test_file = temp_dir / "test.txt"
    test_file.write_text(sample_text)

    open_request = ReaderRequest(
        action=ReaderAction.open, path_or_url=str(test_file)
    )
    open_response = reader_tool.handle_request(open_request)
    doc_id = open_response.doc_info.doc_id

    # Test list_docs
    list_request = ReaderRequest(action=ReaderAction.list_docs)
    list_response = reader_tool.handle_request(list_request)

    assert list_response.success
    assert list_response.doc_list is not None
    assert doc_id in list_response.doc_list

    # Test closing
    close_request = ReaderRequest(action=ReaderAction.close, doc_id=doc_id)
    close_response = reader_tool.handle_request(close_request)

    assert close_response.success

    # Verify document is closed
    list_response = reader_tool.handle_request(list_request)
    assert doc_id not in list_response.doc_list


def test_error_handling(reader_tool):
    """Test error handling for various scenarios."""
    # Test invalid doc_id
    read_request = ReaderRequest(
        action=ReaderAction.read,
        doc_id="NONEXISTENT",
        start_offset=0,
        end_offset=10,
    )
    response = reader_tool.handle_request(read_request)
    assert not response.success
    assert response.error is not None

    # Test missing required fields
    search_request = ReaderRequest(
        action=ReaderAction.search,
        doc_id="NONEXISTENT",
        # Missing search_query
    )
    response = reader_tool.handle_request(search_request)
    assert not response.success
    assert response.error is not None

    # Test invalid file path
    open_request = ReaderRequest(
        action=ReaderAction.open, path_or_url="/nonexistent/path/file.txt"
    )
    response = reader_tool.handle_request(open_request)
    assert response.success  # Should succeed but create empty doc

    # Test invalid chunk parameters
    chunk_request = ReaderRequest(
        action=ReaderAction.chunk_doc,
        doc_id="NONEXISTENT",
        chunk_size=-1,  # Invalid size
        overlap=0.1,
        threshold=5,
    )
    response = reader_tool.handle_request(chunk_request)
    assert not response.success
    assert response.error is not None

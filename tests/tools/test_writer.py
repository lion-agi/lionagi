import json
from pathlib import Path

import pytest

from lionagi.tools.writer.writer import (
    WriterAction,
    WriterDocumentInfo,
    WriterRequest,
    WriterTool,
)


@pytest.fixture
def writer_tool(mock_tempfile, temp_dir):
    """Initialize WriterTool with mocked dependencies."""
    return WriterTool(allowed_root=str(temp_dir))


def test_open_document(
    writer_tool, temp_dir, sample_text, mock_file_operations, mock_tempfile
):
    """Test opening a document."""
    # Test opening with existing file
    test_file = temp_dir / "test.txt"
    test_file.write_text(sample_text)

    request = WriterRequest(action=WriterAction.open, path=str(test_file))
    response = writer_tool.handle_request(request)

    assert response.success
    assert response.doc_info is not None
    assert response.doc_info.doc_id.startswith("WRITER_")
    assert response.doc_info.length == len(sample_text)

    # Test opening without path (new empty doc)
    request = WriterRequest(action=WriterAction.open)
    response = writer_tool.handle_request(request)

    assert response.success
    assert response.doc_info is not None
    assert response.doc_info.length == 0


def test_write_document(
    writer_tool, temp_dir, mock_file_operations, mock_tempfile
):
    """Test writing to a document."""
    # First open a document
    open_request = WriterRequest(action=WriterAction.open)
    open_response = writer_tool.handle_request(open_request)
    doc_id = open_response.doc_info.doc_id

    # Test appending
    append_request = WriterRequest(
        action=WriterAction.write, doc_id=doc_id, content="Hello, World!"
    )
    append_response = writer_tool.handle_request(append_request)

    assert append_response.success
    assert append_response.updated_length == len("Hello, World!")

    # Test writing with offsets
    write_request = WriterRequest(
        action=WriterAction.write,
        doc_id=doc_id,
        content="New",
        start_offset=0,
        end_offset=5,
    )
    write_response = writer_tool.handle_request(write_request)

    assert write_response.success
    assert write_response.updated_length is not None


def test_list_and_close_documents(
    writer_tool, temp_dir, mock_file_operations, mock_tempfile
):
    """Test listing and closing documents."""
    # Open two documents
    doc1_response = writer_tool.handle_request(
        WriterRequest(action=WriterAction.open)
    )
    doc2_response = writer_tool.handle_request(
        WriterRequest(action=WriterAction.open)
    )

    doc1_id = doc1_response.doc_info.doc_id
    doc2_id = doc2_response.doc_info.doc_id

    # Test list_docs
    list_request = WriterRequest(action=WriterAction.list_docs)
    list_response = writer_tool.handle_request(list_request)

    assert list_response.success
    assert list_response.doc_list is not None
    assert doc1_id in list_response.doc_list
    assert doc2_id in list_response.doc_list

    # Test closing
    close_request = WriterRequest(action=WriterAction.close, doc_id=doc1_id)
    close_response = writer_tool.handle_request(close_request)

    assert close_response.success

    # Verify document is closed
    list_response = writer_tool.handle_request(list_request)
    assert doc1_id not in list_response.doc_list
    assert doc2_id in list_response.doc_list


def test_save_file(writer_tool, temp_dir, mock_file_operations, mock_tempfile):
    """Test saving file to disk."""
    content = "Test content to save"
    request = WriterRequest(
        action=WriterAction.save_file,
        directory=str(temp_dir),
        filename="test.txt",
        content=content,
    )
    response = writer_tool.handle_request(request)

    assert response.success
    assert response.saved_path is not None

    # Verify file was saved
    saved_file = Path(response.saved_path)
    assert saved_file.exists()
    assert saved_file.read_text() == content


def test_save_chunks(
    writer_tool, temp_dir, mock_file_operations, mock_tempfile
):
    """Test saving chunks to disk."""
    chunks = [
        {"index": 0, "text": "Chunk 1"},
        {"index": 1, "text": "Chunk 2"},
        {"index": 2, "text": "Chunk 3"},
    ]

    request = WriterRequest(
        action=WriterAction.save_chunks,
        directory=str(temp_dir),
        filename="chunks.json",
        chunks=chunks,
    )
    response = writer_tool.handle_request(request)

    assert response.success
    assert response.saved_path is not None

    # Verify chunks were saved
    saved_file = Path(response.saved_path)
    assert saved_file.exists()
    saved_chunks = json.loads(saved_file.read_text())
    assert len(saved_chunks) == 3
    assert saved_chunks[0]["text"] == "Chunk 1"


def test_path_restrictions(
    writer_tool, temp_dir, mock_file_operations, mock_tempfile
):
    """Test path restriction enforcement."""
    # Try to save outside allowed root
    request = WriterRequest(
        action=WriterAction.save_file,
        directory="/tmp/outside",
        filename="test.txt",
        content="Test",
    )
    response = writer_tool.handle_request(request)

    assert not response.success
    assert response.error is not None
    assert "outside allowed root" in response.error.lower()


def test_error_handling(
    writer_tool, temp_dir, mock_file_operations, mock_tempfile
):
    """Test error handling for various scenarios."""
    # Test invalid doc_id
    write_request = WriterRequest(
        action=WriterAction.write, doc_id="NONEXISTENT", content="test"
    )
    response = writer_tool.handle_request(write_request)
    assert not response.success
    assert response.error is not None

    # Test missing required fields
    save_request = WriterRequest(
        action=WriterAction.save_file,
        directory="/tmp",
        # Missing filename and content
    )
    response = writer_tool.handle_request(save_request)
    assert not response.success
    assert response.error is not None

    # Test invalid offsets
    open_response = writer_tool.handle_request(
        WriterRequest(action=WriterAction.open)
    )
    doc_id = open_response.doc_info.doc_id

    write_request = WriterRequest(
        action=WriterAction.write,
        doc_id=doc_id,
        content="test",
        start_offset=-1,  # Invalid offset
    )
    response = writer_tool.handle_request(write_request)
    assert response.success  # Should handle invalid offset gracefully

    # Test invalid chunks
    chunks_request = WriterRequest(
        action=WriterAction.save_chunks,
        directory="/tmp",
        filename="test.json",
        chunks=None,  # Invalid chunks
    )
    response = writer_tool.handle_request(chunks_request)
    assert not response.success
    assert response.error is not None


def test_document_persistence(
    writer_tool, temp_dir, mock_file_operations, mock_tempfile
):
    """Test document content persistence across operations."""
    # Open and write
    open_response = writer_tool.handle_request(
        WriterRequest(action=WriterAction.open)
    )
    doc_id = open_response.doc_info.doc_id

    content = "Initial content"
    write_response = writer_tool.handle_request(
        WriterRequest(
            action=WriterAction.write, doc_id=doc_id, content=content
        )
    )
    assert write_response.success

    # Save to file
    save_request = WriterRequest(
        action=WriterAction.save_file,
        directory=str(temp_dir),
        filename="persistent.txt",
        content=content,
    )
    save_response = writer_tool.handle_request(save_request)
    assert save_response.success

    # Verify content
    saved_file = Path(save_response.saved_path)
    assert saved_file.exists()
    assert saved_file.read_text() == content

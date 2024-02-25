# from typing import Any
# from lionagi.util import SysUtil, ConvertUtil
# from lionagi.util.import_util import ImportUtil


# def get_llama_index_reader(reader: Any | str = None) -> Any:

#     ImportUtil.check_import('llama-index')
#     import llama_index
#     from llama_index.core import SimpleDirectoryReader
#     from llama_index.core.readers.base import BaseReader


#     if not isinstance(reader, [str, BaseReader]):
#         raise TypeError(f'reader must be a string or BaseReader, not {type(reader)}')

#     if reader in ['SimpleDirectoryReader', SimpleDirectoryReader,
#                   'simple-directory-reader', 'simple_directory_reader', 'simple',
#                   'simple_reader', 'simple-reader']:
#         return SimpleDirectoryReader

#     if isinstance(reader, str):
#         package_name, reader_name = parse_reader_name(reader)

#         try:
#             SysUtil.check_import(package_name)
#             reader = getattr(llama_index.reader, reader_name)
#             return reader

#         except Exception as e:
#             raise AttributeError(f"Failed to import/download {reader}, "
#                                  f"please check llama-index documentation to download it "
#                                  f"manually and input the reader object: {e}")

#     elif isinstance(reader, BaseReader):
#         return reader


# def parse_reader_name(reader_str):
#     reader_ = ''
#     if 'index' in reader_str:
#         reader_ = reader_str.split('index')[-1]

#     reader_ = ConvertUtil.strip_lower(reader_.replace("_", "-"))

#     if reader_.startswith('-'):
#         reader_ = reader_[1:]
#     if reader_.endswith('-'):
#         reader_ = reader_[:-1]
#     if reader_.endswith('reader'):
#         reader_ = reader_[:-6]

#     package_name = f'llama-index-reader-{reader_}'
#     first_letter = reader_[0].upper()

#     reader_name = f"{first_letter}{reader_[1:]}Reader"

#     return package_name, reader_name


# def llama_index_read_data(
#         reader=None, reader_args=None, reader_kwargs=None,
#         loader=None, loader_args=None, loader_kwargs=None):
#     try:
#         reader_args = reader_args or []
#         reader_kwargs = reader_kwargs or {}
#         loader_args = loader_args or []
#         loader_kwargs = loader_kwargs or {}

#         reader = get_llama_index_reader(reader)

#         loader = reader(*reader_args, **reader_kwargs)
#         documents = loader.load_data(*loader_args, **loader_kwargs)
#         return documents
#     except Exception as e:
#         raise ValueError(f'Failed to read and load data. Error: {e}')

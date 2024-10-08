# import pytest

# from lionabc import Observable
# from lionabc.exceptions import LionIDError
# from lion_core.setting import LionIDConfig
# from lion_core.sys_utils import SysUtil


# class TestSysUtilID:
#     def test_id_generation_default(self):
#         id_ = SysUtil.id()
#         assert isinstance(id_, str)
#         assert len(id_) == 48  # 42 chars + prefix "ln" + 4 hyphens
#         assert id_.startswith("ln")
#         assert id_.count("-") == 4

#     def test_id_generation_custom_length(self):
#         id_ = SysUtil.id(n=20)
#         assert len(id_) == 26  # 20 chars + prefix "ln" + 4 hyphens

#     def test_id_generation_no_hyphens(self):
#         id_ = SysUtil.id(random_hyphen=False)
#         assert "-" not in id_
#         assert len(id_) == 44  # 42 chars + prefix "ln"

#     def test_id_generation_custom_prefix_postfix(self):
#         id_ = SysUtil.id(prefix="test_", postfix="_end")
#         assert id_.startswith("test_")
#         assert id_.endswith("_end")

#     def test_id_generation_custom_hyphens(self):
#         id_ = SysUtil.id(
#             num_hyphens=2, hyphen_start_index=10, hyphen_end_index=-10
#         )
#         assert id_.count("-") == 2
#         assert "-" not in id_[:10] and "-" not in id_[-10:]

#     @pytest.mark.parametrize("n", [30, 50])
#     def test_id_generation_various_lengths(self, n):
#         id_ = SysUtil.id(n=n)
#         assert len(id_) == n + 6  # n chars + prefix "ln" + 4 hyphens

#     def test_is_id_valid(self):
#         assert SysUtil.is_id(SysUtil.id())
#         assert SysUtil.is_id(
#             "ln8d7274-45a36cc0-8b89af8b-c5-154c41996cf228d8a5"
#         )
#         assert SysUtil.is_id("a" * 32)  # Backward compatibility

#     def test_is_id_invalid(self):
#         assert not SysUtil.is_id("invalid_id")
#         assert not SysUtil.is_id(123)
#         assert not SysUtil.is_id("")
#         assert not SysUtil.is_id(
#             "ln" + "a" * 42
#         )  # Correct length but no hyphens

#     def test_is_id_custom_config(self):
#         custom_config = LionIDConfig(
#             prefix="custom-",
#             n=20,
#             num_hyphens=2,
#             random_hyphen=True,
#             hyphen_start_index=6,
#             hyphen_end_index=-6,
#         )
#         valid_id = "custom-a32eac2f22a-62-a45092f"
#         assert SysUtil.is_id(valid_id, custom_config)
#         assert not SysUtil.is_id(valid_id)  # Should fail with default config

#     def test_get_id_observable(self):
#         class MockObservable(Observable):
#             def __init__(self, ln_id):
#                 self.ln_id = ln_id

#         valid_id = SysUtil.id()
#         mock_obj = MockObservable(valid_id)
#         assert SysUtil.get_id(mock_obj) == valid_id

#     def test_get_id_string(self):
#         valid_id = SysUtil.id()
#         assert SysUtil.get_id(valid_id) == valid_id
#         assert SysUtil.get_id("a" * 32) == "a" * 32  # Backward compatibility

#     def test_get_id_sequence(self):
#         valid_id = SysUtil.id()
#         assert SysUtil.get_id([valid_id]) == valid_id
#         assert SysUtil.get_id((valid_id,)) == valid_id

#     def test_get_id_invalid(self):
#         with pytest.raises(LionIDError):
#             SysUtil.get_id("invalid_id")
#         with pytest.raises(LionIDError):
#             SysUtil.get_id(123)
#         with pytest.raises(LionIDError):
#             SysUtil.get_id([])

#     def test_get_id_custom_config(self):
#         custom_config = LionIDConfig(
#             prefix="custom-",
#             n=20,
#             num_hyphens=2,
#             random_hyphen=True,
#             hyphen_start_index=6,
#             hyphen_end_index=-6,
#         )
#         custom_id = "custom-a32eac2f22a-62-a45092f"
#         assert SysUtil.get_id(custom_id, custom_config) == custom_id
#         with pytest.raises(LionIDError):
#             SysUtil.get_id(custom_id)  # Should fail with default config

#     @pytest.mark.parametrize("invalid_input", [None, [], {}, set()])
#     def test_get_id_edge_cases(self, invalid_input):
#         with pytest.raises(LionIDError):
#             SysUtil.get_id(invalid_input)

#     def test_id_default(self):
#         id_ = SysUtil.id()
#         assert isinstance(id_, str)
#         assert len(id_) == 48  # 42 chars + prefix "ln" + 4 hyphens

#     def test_id_custom_length(self):
#         id_ = SysUtil.id(n=20)
#         assert len(id_) == 26  # 20 chars + prefix "ln" + 4 hyphens

#     def test_id_no_hyphens(self):
#         id_ = SysUtil.id(random_hyphen=False)
#         assert "-" not in id_

#     def test_id_custom_prefix_postfix(self):
#         id_ = SysUtil.id(prefix="test_", postfix="_end")
#         assert id_.startswith("test_")
#         assert id_.endswith("_end")

#     def test_id_all_options(self):
#         id_ = SysUtil.id(
#             n=30,
#             prefix="custom_",
#             postfix="_end",
#             random_hyphen=True,
#             num_hyphens=3,
#         )
#         assert id_.startswith("custom_")
#         assert id_.endswith("_end")
#         assert id_.count("-") == 3
#         assert (
#             len(id_) == 30 + len("custom_") + len("_end") + 3
#         )  # 30 chars + prefix + postfix + 3 hyphens

#     def test_get_id_valid(self):
#         class MockObservable(Observable):
#             def __init__(self, ln_id):
#                 self.ln_id = ln_id

#         valid_id = SysUtil.id()
#         mock_obj = MockObservable(valid_id)
#         assert SysUtil.get_id(mock_obj) == valid_id
#         assert SysUtil.get_id(valid_id) == valid_id

#     def test_get_id_invalid(self):
#         with pytest.raises(LionIDError):
#             SysUtil.get_id("invalid_id")

#     def test_get_id_sequence(self):
#         valid_id = SysUtil.id()
#         assert SysUtil.get_id([valid_id]) == valid_id

#     def test_get_id_custom_config(self):
#         custom_config = LionIDConfig(
#             prefix="custom-",
#             n=20,
#             num_hyphens=2,
#             random_hyphen=True,
#             hyphen_start_index=6,
#             hyphen_end_index=-6,
#         )
#         valid_id = "custom-a32eac2f22a-62-a45092f"
#         assert SysUtil.get_id(valid_id, custom_config) == valid_id

#     def test_is_id_valid(self):
#         valid_id = "ln8d7274-45a36cc0-8b89af8b-c5-154c41996cf228d8a5"
#         assert SysUtil.is_id(valid_id) == True

#     def test_is_id_invalid(self):
#         invalid_id = "invalid_id"
#         assert SysUtil.is_id(invalid_id) == False

#     def test_is_id_custom_config(self):
#         custom_config = LionIDConfig(
#             prefix="custom-",
#             n=20,
#             num_hyphens=2,
#             random_hyphen=True,
#             hyphen_start_index=6,
#             hyphen_end_index=-6,
#         )
#         valid_id = "custom-a32eac2f22a-62-a45092f"
#         assert SysUtil.is_id(valid_id, custom_config) == True

#     def test_get_id_32_char(self):
#         valid_id = "a" * 32
#         assert SysUtil.get_id(valid_id) == valid_id

#     def test_get_id_invalid_type(self):
#         with pytest.raises(LionIDError):
#             SysUtil.get_id(123)

#     def test_is_id_edge_cases(self):
#         assert SysUtil.is_id("a" * 32) == True
#         assert SysUtil.is_id(123) == False
#         assert SysUtil.is_id("") == False

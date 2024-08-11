# import asyncio
# from api.apicore import _connect as _connect_
# from lionagi.core.tool import ToolManager
# from lionagi import func_to_tool


# async def async_list_s3_bucket_example():
#     """
#     setup an API framework to facilitate the use of tool sets
#     for the first gimmick, we will use the AWS S3 API to demonstrate the its procedure and
#     finally print the buckets in the account
#     """
#     # instantiate the api object, in this case, the AWS S3 object
#     object_api = _connect_.get_object("AWSS3")

#     # instantiate the tool manager
#     tool_manager = ToolManager()

#     # register the tool, bind the function to the tool object
#     tool_manager._register_tool(
#         func_to_tool(object_api.list_bucket_names, docstring_style="google")[0]
#     )

#     # invoke the function in the context of the tool manager, this function doesn't take any arguments
#     response = await tool_manager.invoke(("list_bucket_names", {}))

#     # print the response
#     print("Here are the s3 buckets in the aws account:")
#     from pprint import pprint

#     pprint(response)


# if __name__ == "__main__":
#     asyncio.run(async_list_s3_bucket_example())

LionAGI Introduction 2: Data Processing
=======================================

LionAGI is very efficient and intuitive to handle data

.. code:: ipython3

    from pathlib import Path
    import lionagi as li

.. code:: ipython3

    from timeit import default_timer as timer
    start = timer()

.. code:: ipython3

    ext=[".py", ".ipynb"]
    data_dir = Path.cwd().parent / 'data'
    project_name = "lionagi_intro"

1. Find Path
~~~~~~~~~~~~

.. code:: ipython3

    sources = li.dir_to_path(data_dir, ext, 
                             recursive=True, 
                             flat=False)
    
    print(f"Found {len(sources[0])} files with extension '{ext[0]}' in source directory")
    print(f"Found {len(sources[1])} files with extension '{ext[1]}' in source directory")
    print(f"Found {len(li.to_list(sources, flat=True))} files in total in source directory")


.. parsed-literal::

    Found 1673 files with extension '.py' in source directory
    Found 375 files with extension '.ipynb' in source directory
    Found 2048 files in total in source directory


2. Read Files
~~~~~~~~~~~~~

.. code:: ipython3

    files = li.dir_to_files(data_dir, ext, 
                            recursive=True, 
                            project=project_name, to_csv=True) 
    
    print(f"There are in total {sum(li.l_call(files, lambda x: x['file_size'])):,} chracters in {len(files)} non-empty files")


.. parsed-literal::

    1998 logs saved to data/logs/sources/2023-12-07T16_33_49_428438lionagi_intro_sources.csv
    There are in total 47,597,917 chracters in 1998 non-empty files


.. code:: ipython3

    test = files[50]
    
    print(f"Files are read into {type(test)} type")
    print(f"By default files include {test.keys()}\n\n-------------------------------------------------")
    print(f"Sample from {li.to_list(sources, flat=True)[25]}\n-------------------------------------------------\n")
    print(test['content'][:200])


.. parsed-literal::

    Files are read into <class 'dict'> type
    By default files include dict_keys(['project', 'folder', 'file', 'file_size', 'content'])
    
    -------------------------------------------------
    Sample from /Users/lion/Documents/GitHub/gitco/data/gitrepo/privateGPT-main/private_gpt/server/ingest/ingest_watcher.py
    -------------------------------------------------
    
    import argparse
    import sys
    from pathlib import Path
    
    from private_gpt.di import root_injector
    from private_gpt.server.ingest.ingest_service import IngestService
    from private_gpt.server.ingest.ingest_w


.. code:: ipython3

    lens = li.l_call(files, lambda x: len(x['content']))
    min_, max_, avg_ = min(lens), max(lens), sum(lens)/len(lens)
    
    print(f"Minimum length of files is {min_} in characters")
    print(f"Maximum length of files is {max_:,} in characters")
    print(f"Average length of files is {int(avg_):,} in characters")
    
    print("""
    the files seem to be fairly uneven in terms of length
    which could bring problems in our subsequent analysis, we can stardardize them into chunks 
    one convinient way to do this is via file_to_chunks function, it breaks the files into organized chunks
    """)


.. parsed-literal::

    Minimum length of files is 13 in characters
    Maximum length of files is 11,639,637 in characters
    Average length of files is 23,822 in characters
    
    the files seem to be fairly uneven in terms of length
    which could bring problems in our subsequent analysis, we can stardardize them into chunks 
    one convinient way to do this is via file_to_chunks function, it breaks the files into organized chunks
    


3. Split to chunks
~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    chunks = li.file_to_chunks(files, 
                                chunk_size=1000,  
                                overlap=0.2, 
                                threshold=200, to_csv=True, project=project_name, filename=f"{project_name}_chunks.csv")


.. parsed-literal::

    48277 logs saved to data/logs/sources/2023-12-07T16_33_49_934733lionagi_intro_chunks.csv


.. code:: ipython3

    lens = li.l_call(li.to_list(chunks, flat=True), lambda x: len(x["chunk_content"]))
    min_, max_, avg_ = min(lens), max(lens), sum(lens)/len(lens)
    
    print(f"There are in total {len(li.to_list(chunks,flat=True)):,} chunks")
    print(f"Minimum length of content in chunk is {min_} characters")
    print(f"Maximum length of content in chunk is {max_:,} characters")
    print(f"Average length of content in chunk is {int(avg_):,} characters")
    print(f"There are in total {sum(li.l_call(chunks, lambda x: x['chunk_size'])):,} chracters in total")
    
    print("""
    Though the chunk_size is set to be 1000 in this case, the actual chunk_size depends on a number of factors:
    - if the file is originally shorter than 1000, we will keep whole file as a chunk
    - we will chunk the files by 1000 characters, additionally
        - we add overlap for each chunk with neighbor. For example, if
            - first chunk would have one side of neighbor, it will be 1000 + 1000 * 0.2/2 = 1100
            - second chunk would have two sides of neighbor, it will be 1000 + 1000 * 0.2 = 1200
        - last chunk if longer than threshold, it will be 1000*0.2/2 + remaining length
        - if the remaining length is shorter than threshold, we will merge it with the preceeding chunk
    """)


.. parsed-literal::

    There are in total 48,277 chunks
    Minimum length of content in chunk is 13 characters
    Maximum length of content in chunk is 1,400 characters
    Average length of content in chunk is 1,178 characters
    There are in total 56,874,923 chracters in total
    
    Though the chunk_size is set to be 1000 in this case, the actual chunk_size depends on a number of factors:
    - if the file is originally shorter than 1000, we will keep whole file as a chunk
    - we will chunk the files by 1000 characters, additionally
        - we add overlap for each chunk with neighbor. For example, if
            - first chunk would have one side of neighbor, it will be 1000 + 1000 * 0.2/2 = 1100
            - second chunk would have two sides of neighbor, it will be 1000 + 1000 * 0.2 = 1200
        - last chunk if longer than threshold, it will be 1000*0.2/2 + remaining length
        - if the remaining length is shorter than threshold, we will merge it with the preceeding chunk
    


4. Aggregate into bins
~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    print("""Let's say you conducted certain llm analysis or similar data transformation on the chunks
    and you now you want to put them in groups(bins) of certain range of length """)



.. parsed-literal::

    Let's say you conducted certain llm analysis or similar data transformation on the chunks
    and you now you want to put them in groups(bins) of certain range of length 


.. code:: ipython3

    f = lambda x: x['chunk_content']
    inputs = li.to_list(li.l_call(chunks, f))
    
    bins = li.get_bins(inputs, upper=8000)
    print(f"For bin size of 8000: There are in total {len(bins)} bins")
    
    bins = li.get_bins(inputs, upper=4000)
    print(f"For bin size of 4000: There are in total {len(bins)} bins")
    
    bins = li.get_bins(inputs, upper=2000)
    print(f"For bin size of 2000: There are in total {len(bins)} bins")


.. parsed-literal::

    For bin size of 8000: There are in total 7863 bins
    For bin size of 4000: There are in total 15882 bins
    For bin size of 2000: There are in total 47036 bins


.. code:: ipython3

    elapse = timer() - start

.. code:: ipython3

    print(f"Total files processed {len(files):,}, with {sum(li.l_call(files, lambda x: x['file_size'])):,} chracters of content in total")
    print(f"Total chunks produced {len(chunks):,}, with {sum(li.l_call(chunks, lambda x: x['chunk_size'])):,} chracters of content in total")
    
    print(f"Total runtime: {elapse:.03f} seconds")


.. parsed-literal::

    Total files processed 1,998, with 47,597,917 chracters of content in total
    Total chunks produced 48,277, with 56,874,923 chracters of content in total
    Total runtime: 1.719 seconds


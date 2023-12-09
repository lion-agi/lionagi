LionAGI Introduction 1: Utils
=============================

LionAGI is equipped with a set of powerful system tools

.. code-block:: python

    import lionagi as li

Special function calls
~~~~~~~~~~~~~~~~~~~~~~

Complicated loops and iterations are a pain for large data sets, and
complex data structure

special function call handlers are designed to reduce that pain to stay
focus on the workflow

.. code-block:: python

    # create a test input list
    a = [1,2,3,4,5]
    
    # create some test functions
    f1 = lambda x: x**2

.. code-block:: python

    # the first special function calling method is called l_call (list call)
    # you can operate a single function on the whole set of input list
    
    li.l_call(a, f1)




.. parsed-literal::

    [1, 4, 9, 16, 25]



.. code-block:: python

    # the second is called m_call (map call) 
    # provide a list of inputs and a list of functions of same length
    # output element-wise results,
    
    a = [1,2,3,4,5]
    
    f1 = lambda x: x+1
    f2 = lambda x: x+2
    f3 = lambda x: x+3
    f4 = lambda x: x+4
    f5 = lambda x: x+5
    
    # put these functions into a list
    f = [f1,f2,f3,f4,f5]
    
    li.m_call(a,f)




.. parsed-literal::

    [2, 4, 6, 8, 10]



.. code-block:: python

    # e_call, explode call, it creates a 2-dimensional list
    # of each element applied with each function
    
    li.e_call(a,f)




.. parsed-literal::

    [[2, 3, 4, 5, 6],
     [3, 4, 5, 6, 7],
     [4, 5, 6, 7, 8],
     [5, 6, 7, 8, 9],
     [6, 7, 8, 9, 10]]



Flatten nested dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # get all nested dict outside return as an unnested dict, 
    # preserve parent-child relationship, and key order
    
    a = {
        'aa': 1,
        'bb': {
            'cc': 2,
            'dd': 3
            },
        'ee': {
            'ff': 4,
            'gg': {
                'hh': 5
                }
            }   
        }
    
    li.to_flat_dict(a)




.. parsed-literal::

    {'aa': 1, 'bb_cc': 2, 'bb_dd': 3, 'ee_ff': 4, 'ee_gg_hh': 5}



.. code-block:: python

    li.to_flat_dict(a, sep='.') # change separator




.. parsed-literal::

    {'aa': 1, 'bb.cc': 2, 'bb.dd': 3, 'ee.ff': 4, 'ee.gg.hh': 5}



Type conversion and validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # to_list can convert given object to list with many special features
    
    a1 = [[1,2],[[3],4],5]
    li.to_list(a1, flat=True) # flatten the list




.. parsed-literal::

    [1, 2, 3, 4, 5]



.. code-block:: python

    a1 = [['a',1, [None,2.0]], True]
    
    li.to_list(a1, dropna=True) # also drop None




.. parsed-literal::

    ['a', 1, 2.0, True]



.. code-block:: python

    # combining to_list calls using different features can be very powerful
    a1 = [['a',1, [None, 2.0]], True] + li.to_list(a, flatten_dict=True)
    
    li.to_list(a1, flat=True, dropna=False)




.. parsed-literal::

    ['a',
     1,
     None,
     2.0,
     True,
     {'aa': 1},
     {'bb_cc': 2},
     {'bb_dd': 3},
     {'ee_ff': 4},
     {'ee_gg_hh': 5}]



.. code-block:: python

    # keep all numeric from a string return as a positive int (will have error if encouter .)
    li.str_to_num('1d24e', upper_bound=100, lower_bound=1)




.. parsed-literal::

    1



.. code-block:: python

    # keep all numeric from a string return as a positive float (. must be behind a number immiediately)
    li.str_to_num('1d2.4df21234257e', upper_bound=100, lower_bound=0, num_type=float, precision=3)




.. parsed-literal::

    1.0



Others
~~~~~~

.. code-block:: python

    # create deep copies of any object
    li.make_copy(a,3)




.. parsed-literal::

    [{'aa': 1, 'bb': {'cc': 2, 'dd': 3}, 'ee': {'ff': 4, 'gg': {'hh': 5}}},
     {'aa': 1, 'bb': {'cc': 2, 'dd': 3}, 'ee': {'ff': 4, 'gg': {'hh': 5}}},
     {'aa': 1, 'bb': {'cc': 2, 'dd': 3}, 'ee': {'ff': 4, 'gg': {'hh': 5}}}]



.. code-block:: python

    len(a)




.. parsed-literal::

    3



.. code-block:: python

    f = lambda x: li.to_flat_dict(a, sep='.')
    li.hold_call(a, f, sleep=1)




.. parsed-literal::

    {'aa': 1, 'bb.cc': 2, 'bb.dd': 3, 'ee.ff': 4, 'ee.gg.hh': 5}



.. code-block:: python

    def ff(x):
        raise Exception('test')
    
    li.hold_call(a, ff, sleep=1, ignore_error=True, message='exception ignored ')


.. parsed-literal::

    exception ignored  Error: test


.. code-block:: python

    li.hold_call(a, ff, sleep=1, ignore_error=False, message='exception not ignored ')


.. parsed-literal::

    exception not ignored  Error: test


::


    ---------------------------------------------------------------------------

    Exception                                 Traceback (most recent call last)

    Cell In[17], line 1
    ----> 1 li.hold_call(a, ff, sleep=1, ignore_error=False, message='exception not ignored ')


    File ~/Documents/GitHub/lionagi/lionagi/utils/sys_util.py:368, in hold_call(input, func, sleep, message, ignore_error, **kwargs)
        366 try:
        367     time.sleep(sleep)
    --> 368     return func(input, **kwargs)
        369 except Exception as e:
        370     if message:


    Cell In[16], line 2, in ff(x)
          1 def ff(x):
    ----> 2     raise Exception('test')


    Exception: test


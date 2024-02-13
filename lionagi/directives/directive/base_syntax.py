"""
# basic syntax
executeAction(param1, param2) IF condition1 && condition2 || !condition3;

# verb
DO

# logic operator

AND: &&
OR: ||
NOT: !
GREATER_THAN: >
LESS_THAN: <
GREATER_THAN_OR_EQUAL: >=
LESS_THAN_OR_EQUAL: <=
EQUAL: ==
NOT_EQUAL: !=

# conditions
IF
ELIF
ELSE

# loop
FOR 
IN

# EXCEPTION
TRY 
EXCEPT

"""


"""
DO: perform a single action
THEN: extend directive to include more statment
IF: condition

FOR
IN
END
BEGIN

TRY
EXCEPT

---

COMPOSE; - indicate the beginning of a script-like block to execute 
THEN; - indicate continuation of a script-like block, another statement to execute
RUN; - indicate the end of script-like block, and let the script execute


XX;  ; END XX;



TRY; DO ACTION_A; END TRY; 



COMPOSE;
IF CONDITION_A; DO ACTION_B;        -
THEN TRY; DO ACTION_C ENDTRY;         
THEN EXCEPT; IF CONDITION_C; DO ACTION_D; ENDEXCEPT; 
THEN FOR ITEM IN COLLECTION; DO ACTION_E(item.param1, item.param2); ENDFOR
RUN;


 

DO ACTION B; 




IF 
THEN




GROUP





"""






"""syntax:


BEGIN; IF condition1 && condition2 || !condition3; THEN DO action(param1, param2); END IF; END;

BEGIN; FOR item IN collection; DO action(item.param1, item.param2); END FOR; END;

BEGIN; DO action1(param1, param2); DO action2(param3, param4); END GROUP; END;


"""





"""
FOR item IN collection DO
    executeAction(item.param1, item.param2);
END FOR;
"""

"""
BEGIN
    executeAction1(param1, param2);
    IF condition2 THEN executeAction2(param3, param4);
    FOR item IN collection DO
        executeAction3(item.param1, item.param2);
    END FOR;
END;
"""


"""
TRY
    executeAction(param1, param2);
EXCEPT
    handleErrorAction(param1, param2);
"""
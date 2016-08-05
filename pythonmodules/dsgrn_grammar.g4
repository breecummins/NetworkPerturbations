grammar DSGRN;

network:
    statement ('\n' statement )*
    ;

statement:
    ident ':' expr;

expr
    : term
    | '(' expr ')' term
    | term '(' expr ')'
    | '(' expr ')' '(' expr ')'
    | expr '+' expr
    ;

ident:
    (CHAR)+
    ;

CHAR
    :[a-zA-Z0-9]
    ;

term: '~'? ident;

WS: 
    [ \t\n\r] + -> skip
    ;

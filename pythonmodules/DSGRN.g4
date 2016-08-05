grammar DSGRN;

network:
    statement ('\n' statement )*
    ;

statement:
    ident ':' expr
    | ident ':' expr ': E'
    ;

expr: 
    term
    | '(' expr ')' term
    | term '(' expr ')'
    | '(' expr ')' '(' expr ')'
    | expr '+' expr
    ;

ident:
    (CHAR)+
    ;

CHAR
    :[a-zA-Z0-9_]
    ;

term: '~'? ident;

WS: 
    [ \t\n\r] + -> skip
    ;

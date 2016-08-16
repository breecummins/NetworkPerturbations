grammar DSGRN;

/* options {
    language = Python2; 
} */



/* Lexer rules */

@lexer::members {
    boolean ignore=true;
}

/* White space is active for multiplication, otherwise ignored */
MULT_WS : [ \t] { ignore = false; } [\n\r] { ignore = true; } WS { ignore = true; };

CHAR: [a-zA-Z0-9_];

WS: [ \t\n\r] + { if(ignore) skip(); } ;




/* Parser rules */

network:
    statement (('\n')+ statement)* ('\n')* EOF  /* EOF needed to parse everything */
    ;

statement:
    ident ':' expr (essential)?
    ;

ident:    /* could be lexer rule but want on parse tree */
    (CHAR)+
    ;

essential:    /* could be lexer rule (with white space modification) but want on parse tree */
    ':' 'E'  
    ;

expr:       /* another option is "expr: sum | mult;" but that leads to a longer parse tree */
    term 
    | enclosed_term
    | sum 
    | enclosed_sum
    | mult
    ;

term: 
    ('~')? ident
    ;

enclosed_term:      /* can have parentheses/nested parentheses */
    '(' term ')'
    | '(' enclosed_term ')'
    ;

sum:
    ( term | enclosed_term) ('+' ( term | enclosed_term))*    /* at least one term */
    ;

enclosed_sum:     /* parentheses/nested parentheses are required for mult, but optional for expr */
    '(' sum ')'
    | '(' enclosed_sum ')' 
    ;

mult:
    term ((MULT_WS)+ term)*   /* active white space parsed first */
    | enclosed_sum
/*    | (term | enclosed_sum) ('*')? enclosed_sum  */
/*    | enclosed_sum ('*')? term  */
    | mult (MULT_WS)+ mult     /* active white space parsed first */
    | mult ('*')? mult         /* explicit or missing mult sign parsed second */
    | '(' mult ')'             /* can have parentheses/nested parentheses */
    ;

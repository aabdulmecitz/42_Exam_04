// SINAV ESNASINDA YAZILACAK: level3/vbc/vbc.c
// SADECE EKSIK PARSER FONKSIYONLARI YAZILACAK - given.c mevcut

#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>


// BU FONKSIYONLARI YAZMANIZ GEREKIYOR:

node *parse_expr(char **s) {
    node *left = parse_term(s);
    if (!left)
        return (NULL);
    while (accept(s, '+')) {
        node *right = parse_term(s);
        if (!right) {
            destroy_tree(left);
            return (NULL);
        }
        node n = {ADD, 0, left, right};
        left = new_node(n);
        if (!left) {
            destroy_tree(right);
            return (NULL);
        }
    }
    return (left);
}

node *parse_term(char **s) {
    node *left = parse_factor(s);
    if (!left)
        return (NULL);
    while (accept(s, '*')) {
        node *right = parse_factor(s);
        if (!right) {
            destroy_tree(left);
            return (NULL);
        }
        node n = {MULTI, 0, left, right};
        left = new_node(n);
        if (!left) {
            destroy_tree(right);
            return (NULL);
        }
    }
    return (left);
}

node *parse_factor(char **s) {
    if (isdigit(**s)) {
        node n = {VAL, **s - '0', NULL, NULL};
        (*s)++;
        return (new_node(n));
    }
    if (accept(s, '('))
    {
        node *n = parse_expr(s);
        if (!expect(s, ')')) {
            destroy_tree(n);
            return (NULL);
        }
        return (n);
    }
    unexpected(**s);
    return (NULL);
}


# chomsky.converterLFA
Given a context-free grammar (GLC) G, transforms it into an equivalent GLC G' in Chomsky normal form.

## Formal definition of a GLC
``GLC G: (V,Σ,R,P), ∀R: (X → w) ∧ (X ∈ V) ∧ (w ∈ (V ∪ Σ)^*)``

in short: the production(w) of every rule(R) might be any combination of the language's alphabet(Σ) and variables(V). 

## Formal definition of Chomsky's Normal Form
``GLC in CNF G': (V, Σ, R, P), if λ ∈ L(G') then P → λ, ∀R: (X → YZ for X, Y, Z ∈ V) ∨ (X → a for a ∈ Σ)``

in short: the initial variable(P) generates lambda(λ) if its contained by the language, and all of the other rules must either product exactly two more rules(YZ) concatenated or a simbol(a) of the alphabet(Σ).

## How does the conversion works

There are several manipulations of a GLC which doesn't alter the generated language, although restructures the grammar rules productions. When applying multiple types of deletions in sequence, some rule types that have already been deleted may reappear, in order to avoid it there is a carefully defined sequence procedure to preserve elimination **consistency**(before and after):

![step1](https://github.com/MnoZombie956/chomsky.converterLFA/blob/main/materials/step1.png?raw=false)

![step2](https://github.com/MnoZombie956/chomsky.converterLFA/blob/main/materials/step2.png?raw=false)

![step3](https://github.com/MnoZombie956/chomsky.converterLFA/blob/main/materials/step3.png?raw=false)

![step4](https://github.com/MnoZombie956/chomsky.converterLFA/blob/main/materials/step4.png?raw=false)

![step5](https://github.com/MnoZombie956/chomsky.converterLFA/blob/main/materials/step5.png?raw=false)

## Running the test cases
``
python3 chomsky.py G.json
``

## More stuff

Try to convert a CFG to Greibach's Normal Form(GNF)!

``GLC in GNF G'' = (V, Σ, R, P), if λ ∈ L(G'') then P → λ, ∀R: X → ay for a ∈ Σ and y ∈ V^*``

in short: the initial variable(P) generates lambda(λ) if its contained by the language, and all of the other rules must product exactly one simbol(a) of the alphabet(Σ) followed by any combination of other rules(y) concatenated.


How to? Have a peek of the methods:
- Elimination of left recursive rules.
- Variable in Rule elimination.

### Bibliography:
1. Hopcroft J., Motwani R. Ullman J.; Introduction to Automata Theory, Languages, and Computation; 3rd edition, 2006.

2. Vieira N.; Introdução aos Fundamentos da Computação; 1a edição, 2006.

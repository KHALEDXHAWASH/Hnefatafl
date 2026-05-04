:- use_module(library(lists)).
:- use_module(library(aggregate)).

initial_board(
    [[c, e, e, a, a, a, a, a, e, e, c],
     [e, e, e, e, e, a, e, e, e, e, e],
     [e, e, e, e, e, e, e, e, e, e, e],
     [a, e, e, e, e, d, e, e, e, e, a],
     [a, e, e, e, d, d, d, e, e, e, a],
     [a, a, e, d, d, k, d, d, e, a, a],
     [a, e, e, e, d, d, d, e, e, e, a],
     [a, e, e, e, e, d, e, e, e, e, a],
     [e, e, e, e, e, e, e, e, e, e, e],
     [e, e, e, e, e, a, e, e, e, e, e],
     [c, e, e, a, a, a, a, a, e, e, c]]).

size(11).
center(5, 5).
corner(0,  0).
corner(0,  10).
corner(10, 0).
corner(10, 10).

nth0_list(0, [H|_], H) :- !.
nth0_list(N, [_|T], V) :-
    N > 0,
    N1 is N - 1,
    nth0_list(N1, T, V).

set_nth0(0, [_|T], V, [V|T]) :- !.
set_nth0(N, [H|T], V, [H|T2]) :-
    N > 0,
    N1 is N - 1,
    set_nth0(N1, T, V, T2).

cell(Board, R, C, V) :-
    nth0_list(R, Board, Row),
    nth0_list(C, Row, V).

set_cell(Board, R, C, V, NewBoard) :-
    nth0_list(R, Board, Row),
    set_nth0(C, Row, V, NewRow),
    set_nth0(R, Board, NewRow, NewBoard).

inbound(R, C) :-
    size(S),
    R >= 0, R < S,
    C >= 0, C < S.

find_king(Board, KR, KC) :-
    size(S),
    Max is S - 1,
    between(0, Max, KR),
    between(0, Max, KC),
    cell(Board, KR, KC, k),
    !.

enemy(a, d).
enemy(d, a).
enemy(k, a).

is_ally(a, a).
is_ally(d, d).
is_ally(k, d).
is_ally(d, k).

throne_or_corner(R, C) :- center(R, C).
throne_or_corner(R, C) :- corner(R, C).

is_blocking_for_king(Board, R, C) :-
    ( \+ inbound(R, C) -> true
    ; cell(Board, R, C, a) -> true
    ; throne_or_corner(R, C)
    ).
inside_sandwich(Board, R, C, Piece) :-
    Piece \= k,
    ( Piece = a -> Enemy = d ; Enemy = a ),
    (
        C_Left is C - 1, inbound(R, C_Left), cell(Board, R, C_Left, Enemy),
        C_Right is C + 1, inbound(R, C_Right), cell(Board, R, C_Right, Enemy)
    ;
        R_Up is R - 1, inbound(R_Up, C), cell(Board, R_Up, C, Enemy),
        R_Down is R + 1, inbound(R_Down, C), cell(Board, R_Down, C, Enemy)
    ).

isvalidmove(Board, R, C, NR, NC) :-
    cell(Board, R, C, Piece),
    Piece \= e,
    Piece \= c,
    inbound(NR, NC),
    ( corner(NR, NC) -> Piece = k ; true ),
    ( center(NR, NC) -> Piece = k ; true ),
    cell(Board, NR, NC, Dest),
    ( Dest = e ; (Piece = k, Dest = c) ),
    \+ inside_sandwich(Board, NR, NC, Piece),
    ( R =:= NR ->
        (NC > C -> Step = 1 ; Step = -1),
        C1 is C + Step,
        path_clear_col(Board, R, C1, NC, Step)
    ; C =:= NC ->
        (NR > R -> Step = 1 ; Step = -1),
        R1 is R + Step,
        path_clear_row(Board, R1, NR, NC, Step)
    ).

path_clear_col(_, _, C, C, _) :- !.
path_clear_col(Board, R, Cur, End, Step) :-
    cell(Board, R, Cur, e),
    Next is Cur + Step,
    path_clear_col(Board, R, Next, End, Step).

path_clear_row(_, R, R, _, _) :- !.
path_clear_row(Board, Cur, End, C, Step) :-
    cell(Board, Cur, C, e),
    Next is Cur + Step,
    path_clear_row(Board, Next, End, C, Step).

apply_move(Board, R, C, NR, NC, Board2) :-
    cell(Board, R, C, Piece),
    set_cell(Board, R,  C,  e,     B1),
    set_cell(B1,   NR, NC, Piece, Board2).

simulate_move(Board, R, C, NR, NC, FinalBoard) :-
    apply_move(Board, R, C, NR, NC, B1),
    perform_captures(B1, NR, NC, B2),
    capture_king(B2, FinalBoard).

move(Board, R, C, NR, NC, FinalBoard) :-
    ( isvalidmove(Board, R, C, NR, NC) ->
        simulate_move(Board, R, C, NR, NC, FinalBoard)
    ;
        write('Invalid move.'), nl,
        FinalBoard = Board
    ).

perform_captures(Board, R, C, FinalBoard) :-
    cell(Board, R, C, Piece),
    ( Piece = k ->
        FinalBoard = Board
    ;
        ( Piece = a -> Enemy = d ; Enemy = a ),
        Dirs = [(-1,0),(1,0),(0,-1),(0,1)],
        foldl(try_custodial(Board, R, C, Piece, Enemy), Dirs, Board, FinalBoard)
    ).

try_custodial(_OrigBoard, R, C, Piece, Enemy, (DR, DC), Acc, NewAcc) :-
    R1 is R + DR, C1 is C + DC,
    R2 is R + 2*DR, C2 is C + 2*DC,
    ( inbound(R1, C1),
      cell(Acc, R1, C1, Enemy),
      inbound(R2, C2),
      ( cell(Acc, R2, C2, Piece)
      ; ( center(R2, C2),
    cell(Acc, R2, C2, e)
   )
; corner(R2, C2)
)
    ->
        set_cell(Acc, R1, C1, e, NewAcc)
    ;
        NewAcc = Acc
    ).

capture_king(Board, FinalBoard) :-
    ( find_king(Board, KR, KC) ->
        Dirs = [(-1,0),(1,0),(0,-1),(0,1)],
        ( all_sides_closed(Board, KR, KC, Dirs) ->
            set_cell(Board, KR, KC, e, FinalBoard)
        ;
            FinalBoard = Board
        )
    ;
        FinalBoard = Board
    ).

all_sides_closed(_, _, _, []).
all_sides_closed(Board, KR, KC, [(DR,DC)|T]) :-
    NR is KR + DR, NC is KC + DC,
    is_blocking_for_king(Board, NR, NC),
    all_sides_closed(Board, KR, KC, T).

get_winner(Board, Winner) :-
    ( \+ find_king(Board, _, _) ->
        Winner = a
    ;
        find_king(Board, KR, KC),
        ( corner(KR, KC) ->
            Winner = d
        ;
            Winner = none
        )
    ).

game_end(Board) :-
    get_winner(Board, W),
    W \= none.

get_all_moves(Board, Player, Moves) :-
    size(S), Max is S - 1,
    findall((R,C,NR,NC),
        ( between(0, Max, R),
          between(0, Max, C),
          cell(Board, R, C, Piece),
          piece_belongs_to(Piece, Player),
          between(0, Max, NR),
          between(0, Max, NC),
          isvalidmove(Board, R, C, NR, NC)
        ),
        Moves).

piece_belongs_to(a, a).
piece_belongs_to(d, d).
piece_belongs_to(k, d).

alphabeta(Board, 0, _Alpha, _Beta, _, Score) :-
    !,
    eval(Board, Score).
alphabeta(Board, _, _, _, _, Score) :-
    game_end(Board),
    !,
    eval(Board, Score).

alphabeta(Board, Depth, Alpha, Beta, max, Score) :-
    get_all_moves(Board, a, Moves),
    Moves \= [],
    !,
    D1 is Depth - 1,
    max_value(Board, Moves, D1, Alpha, Beta, Score).
alphabeta(Board, _, _, _, max, Score) :-
    eval(Board, Score).

alphabeta(Board, Depth, Alpha, Beta, min, Score) :-
    get_all_moves(Board, d, Moves),
    Moves \= [],
    !,
    D1 is Depth - 1,
    min_value(Board, Moves, D1, Alpha, Beta, Score).
alphabeta(Board, _, _, _, min, Score) :-
    eval(Board, Score).

max_value(_, [], _, Alpha, _, Alpha).
max_value(Board, [(R,C,NR,NC)|Rest], Depth, Alpha, Beta, Score) :-
    simulate_move(Board, R, C, NR, NC, Child),
    alphabeta(Child, Depth, Alpha, Beta, min, ChildScore),
    NewAlpha is max(Alpha, ChildScore),
    ( NewAlpha >= Beta ->
        Score = NewAlpha
    ;
        max_value(Board, Rest, Depth, NewAlpha, Beta, Score)
    ).

min_value(_, [], _, _, Beta, Beta).
min_value(Board, [(R,C,NR,NC)|Rest], Depth, Alpha, Beta, Score) :-
    simulate_move(Board, R, C, NR, NC, Child),
    alphabeta(Child, Depth, Alpha, Beta, max, ChildScore),
    NewBeta is min(Beta, ChildScore),
    ( Alpha >= NewBeta ->
        Score = NewBeta
    ;
        min_value(Board, Rest, Depth, Alpha, NewBeta, Score)
    ).

best_move(Board, Depth, a, BestMove) :-
    get_all_moves(Board, a, [First|Rest]),
    D1 is Depth - 1,
    simulate_move(Board, First, Child0),
    alphabeta(Child0, D1, -100000, 100000, min, Score0),
    find_best_max(Board, Rest, D1, Score0, First, BestMove).

best_move(Board, Depth, d, BestMove) :-
    get_all_moves(Board, d, [First|Rest]),
    D1 is Depth - 1,
    simulate_move(Board, First, Child0),
    alphabeta(Child0, D1, -100000, 100000, max, Score0),
    find_best_min(Board, Rest, D1, Score0, First, BestMove).

simulate_move(Board, (R,C,NR,NC), NewBoard) :-
    simulate_move(Board, R, C, NR, NC, NewBoard).

find_best_max(_, [], _, _, Best, Best).
find_best_max(Board, [Move|Rest], Depth, BestVal, BestSoFar, BestMove) :-
    simulate_move(Board, Move, Child),
    alphabeta(Child, Depth, -100000, 100000, min, Score),
    ( Score > BestVal ->
        find_best_max(Board, Rest, Depth, Score, Move, BestMove)
    ;
        find_best_max(Board, Rest, Depth, BestVal, BestSoFar, BestMove)
    ).

find_best_min(_, [], _, _, Best, Best).
find_best_min(Board, [Move|Rest], Depth, BestVal, BestSoFar, BestMove) :-
    simulate_move(Board, Move, Child),
    alphabeta(Child, Depth, -100000, 100000, max, Score),
    ( Score < BestVal ->
        find_best_min(Board, Rest, Depth, Score, Move, BestMove)
    ;
        find_best_min(Board, Rest, Depth, BestVal, BestSoFar, BestMove)
    ).

eval(Board, Score) :-
    ( \+ find_king(Board, _, _) ->
        Score = 10000
    ;
        find_king(Board, KR, KC),
        ( corner(KR, KC) ->
            Score = -10000
        ;
            count_pieces(Board, a, AC),
            count_pieces(Board, d, DC),
            PieceScore is (AC - DC) * 10,
            Corners = [(0,0),(0,10),(10,0),(10,10)],
            findall(D, (member((CR,CC), Corners), D is abs(KR-CR)+abs(KC-CC)), Dists),
            min_list(Dists, MinDist),
            DistScore is MinDist * 5,
            count_adjacent_attackers(Board, KR, KC, AdjCount),
            AdjScore is AdjCount * 15,
            Score is PieceScore + DistScore + AdjScore
        )
    ).

count_pieces(Board, Piece, Count) :-
    size(S), Max is S - 1,
    findall(1, (between(0, Max, R), between(0, Max, C), cell(Board, R, C, Piece)), Ls),
    length(Ls, Count).

count_adjacent_attackers(Board, KR, KC, Count) :-
    Dirs = [(-1,0),(1,0),(0,-1),(0,1)],
    findall(1,
        ( member((DR,DC), Dirs),
          NR is KR+DR, NC is KC+DC,
          inbound(NR, NC),
          cell(Board, NR, NC, a)
        ),
        Ls),
    length(Ls, Count).

print_board(Board) :-
    nl,
    write('    '), print_col_numbers(0), nl,
    write('   +'), print_horizontal_line(11), write('+'), nl,
    print_rows_pretty(Board, 0),
    write('   +'), print_horizontal_line(11), write('+'), nl, nl.


print_col_numbers(11) :- !.
print_col_numbers(C) :-
    format('~2w ', [C]),
    C1 is C + 1,
    print_col_numbers(C1).


print_horizontal_line(0) :- !.
print_horizontal_line(N) :-
    write('---'),
    N1 is N - 1,
    print_horizontal_line(N1).


print_rows_pretty(_, 11) :- !.
print_rows_pretty(Board, R) :-
    format('~2w | ', [R]),
    nth0_list(R, Board, Row),
    print_pretty_row(Row),
    write('|'), nl,
    R1 is R + 1,
    print_rows_pretty(Board, R1).


print_pretty_row([]).
print_pretty_row([H|T]) :-
    pretty_symbol(H, S),
    format('~w  ', [S]),
    print_pretty_row(T).


pretty_symbol(e, '.').
pretty_symbol(a, 'A').
pretty_symbol(d, 'D').
pretty_symbol(k, 'K').
pretty_symbol(c, 'C').

difficulty_depth(1, 1).
difficulty_depth(2, 3).
difficulty_depth(3, 5).

read_int(Prompt, Valid, Value) :-
    repeat,
        write(Prompt),
        read(Input),
        ( integer(Input), member(Input, Valid) ->
            Value = Input, !
        ;
            write('Please enter one of: '), write(Valid), nl, fail
        ).

read_atom(Prompt, Valid, Value) :-
    repeat,
        write(Prompt),
        read(Input),
        ( member(Input, Valid) ->
            Value = Input, !
        ;
            write('Please enter one of: '), write(Valid), nl, fail
        ).

play :-
    write('============================================='), nl,
    write('       HNEFATAFL  -  Viking Chess'), nl,
    write('============================================='), nl, nl,
    write('Choose difficulty level:'), nl,
    write('  1 -> Easy   (depth 1)'), nl,
    write('  2 -> Medium (depth 3)'), nl,
    write('  3 -> Hard   (depth 5)'), nl,
    read_int('Your choice: ', [1,2,3], Diff),
    difficulty_depth(Diff, Depth), nl,
    write('Choose your side:'), nl,
    write('  a -> Attacker  (moves FIRST)'), nl,
    write('  d -> Defender  (protects the King)'), nl,
    read_atom('Your choice (a/d): ', [a,d], Human),
    ( Human = a -> Computer = d ; Computer = a ), nl,
    initial_board(Board),
    write('Board legend:  a=Attacker  d=Defender  k=King  c=Corner  e=Empty'), nl, nl,
    game_loop(Board, a, Human, Computer, Depth).

game_loop(Board, Current, Human, Computer, Depth) :-
    ( game_end(Board) ->
        print_board(Board),
        get_winner(Board, Winner),
        write('============================================='), nl,
        ( Winner = a ->
            write('GAME OVER - Attackers win! (King captured)')
        ; Winner = d ->
            write('GAME OVER - Defenders win! (King escaped)')
        ;
            write('GAME OVER')
        ), nl,
        write('============================================='), nl
    ;
        print_board(Board),
        ( Current = a -> Label = 'Attacker' ; Label = 'Defender' ),
        ( Current = Human -> Turn = '(YOU)' ; Turn = '(COMPUTER)' ),
        format('--- ~w turn ~w ---~n', [Label, Turn]),
        ( Current = Human ->
            human_turn(Board, Human, NewBoard)
        ;
            computer_turn(Board, Computer, Depth, NewBoard)
        ),
        ( Current = a -> Next = d ; Next = a ),
        game_loop(NewBoard, Next, Human, Computer, Depth)
    ).

human_turn(Board, _Human, NewBoard) :-
    repeat,
        write('Enter move (FromRow FromCol ToRow ToCol): '),
        read((R, C, NR, NC)),
        ( isvalidmove(Board, R, C, NR, NC) ->
            simulate_move(Board, R, C, NR, NC, NewBoard), !
        ;
            write('Invalid move. Try again.'), nl, fail
        ).

computer_turn(Board, Computer, Depth, NewBoard) :-
    write('Computer is thinking...'), nl,
    ( best_move(Board, Depth, Computer, (R,C,NR,NC)) ->
        format('Computer moved: (~w,~w) -> (~w,~w)~n', [R,C,NR,NC]),
        simulate_move(Board, R, C, NR, NC, NewBoard)
    ;
        write('Computer has no valid moves!'), nl,
        NewBoard = Board
    ).

:- initialization(play, main).

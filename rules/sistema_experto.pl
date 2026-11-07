% =====================================================================
% Sistema experto agronómico (Programación Lógica)
% =====================================================================

% ---------- HECHOS ----------
% cultivo(Nombre, PhMinimo, PhMaximo)
cultivo(maiz,   5.8, 7.0).
cultivo(frijol, 6.0, 7.5).
cultivo(tomate, 6.0, 6.8).
cultivo(papa,   5.0, 6.5).
cultivo(arroz,  5.5, 6.5).

% suelo_apto(Cultivo, TipoDeSuelo)
suelo_apto(maiz,   franco).
suelo_apto(maiz,   arcilloso).
suelo_apto(frijol, franco).
suelo_apto(frijol, arenoso).
suelo_apto(tomate, franco).
suelo_apto(tomate, arenoso).
suelo_apto(papa,   franco).
suelo_apto(papa,   arenoso).
suelo_apto(papa,   limoso).
suelo_apto(arroz,  arcilloso).
suelo_apto(arroz,  limoso).

% ---------- REGLAS: APROBACIÓN DE SIEMBRA ----------
% El pH del lote está dentro del rango del cultivo.
ph_compatible(Cultivo, Ph) :-
    cultivo(Cultivo, Min, Max),
    Ph >= Min,
    Ph =< Max.

% Se puede sembrar si el pH y el tipo de suelo son compatibles.
puede_sembrar(Cultivo, Ph, Suelo) :-
    ph_compatible(Cultivo, Ph),
    suelo_apto(Cultivo, Suelo).

% Si NO se puede sembrar, explica el motivo (solo responde cuando hay problema).
motivo_rechazo(Cultivo, _, _, cultivo_desconocido) :-
    \+ cultivo(Cultivo, _, _), !.
motivo_rechazo(Cultivo, Ph, _, ph_fuera_de_rango) :-
    \+ ph_compatible(Cultivo, Ph), !.
motivo_rechazo(Cultivo, _, Suelo, suelo_no_apto) :-
    \+ suelo_apto(Cultivo, Suelo).
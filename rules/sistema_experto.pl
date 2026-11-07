% =====================================================================
% Sistema experto agronómico (Programación Lógica)
% =====================================================================

% ---------------------------------------------------------------------
% HECHOS: cultivos
% ---------------------------------------------------------------------
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

% ---------------------------------------------------------------------
% REGLAS: aprobación de siembra
% ---------------------------------------------------------------------
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

% ---------------------------------------------------------------------
% HECHOS: riego y fertirriego
% ---------------------------------------------------------------------
% humedad_ideal(Etapa, Minimo, Maximo)   (% de humedad del suelo)
humedad_ideal(germinacion,    60, 80).
humedad_ideal(vegetativa,     50, 70).
humedad_ideal(floracion,      55, 75).
humedad_ideal(fructificacion, 50, 70).
humedad_ideal(cosecha,        30, 50).

% nutriente_etapa(Etapa, Nutriente que más conviene aportar en esa etapa)
nutriente_etapa(germinacion,    fosforo).
nutriente_etapa(vegetativa,     nitrogeno).
nutriente_etapa(floracion,      fosforo_potasio).
nutriente_etapa(fructificacion, potasio).
nutriente_etapa(cosecha,        ninguno).

% accion_riego(EstadoHumedad, Clima, Accion, Severidad)
accion_riego(bajo,     calido,   riego_inmediato_abundante,            alta).
accion_riego(bajo,     templado, riego_inmediato,                      media).
accion_riego(bajo,     frio,     riego_ligero,                         media).
accion_riego(adecuado, calido,   mantener_riego_y_vigilar_evaporacion, baja).
accion_riego(adecuado, templado, mantener_riego_actual,                baja).
accion_riego(adecuado, frio,     mantener_riego_actual,                baja).
accion_riego(alto,     _,        suspender_riego_y_revisar_drenaje,    media).

% ---------------------------------------------------------------------
% REGLAS: riego y fertirriego
% ---------------------------------------------------------------------
% Compara la humedad del suelo con el rango ideal de la etapa.
estado_humedad(Etapa, Humedad, bajo) :-
    humedad_ideal(Etapa, Min, _),
    Humedad < Min.
estado_humedad(Etapa, Humedad, adecuado) :-
    humedad_ideal(Etapa, Min, Max),
    Humedad >= Min,
    Humedad =< Max.
estado_humedad(Etapa, Humedad, alto) :-
    humedad_ideal(Etapa, _, Max),
    Humedad > Max.

% Clasifica la temperatura (grados centígrados).
clima(Temp, frio)     :- Temp < 15.
clima(Temp, templado) :- Temp >= 15, Temp < 30.
clima(Temp, calido)   :- Temp >= 30.

% Diagnóstico completo: etapa + humedad + temperatura.
diagnostico_riego(Etapa, Humedad, Temp, Accion, Nutriente, Severidad) :-
    estado_humedad(Etapa, Humedad, Estado),
    clima(Temp, Clima),
    accion_riego(Estado, Clima, Accion, Severidad),
    nutriente_etapa(Etapa, Nutriente).

% ---------------------------------------------------------------------
% HECHOS: plagas, enfermedades y deficiencias
% ---------------------------------------------------------------------
% sintoma(Sintoma): lo que el usuario puede observar en la planta.
sintoma(hojas_amarillas).
sintoma(hojas_moradas).
sintoma(venas_verdes).
sintoma(bordes_quemados).
sintoma(crecimiento_lento).
sintoma(hojas_viejas_primero).
sintoma(hojas_nuevas_primero).
sintoma(hojas_enrolladas).
sintoma(melaza_pegajosa).
sintoma(insectos_blancos).
sintoma(hojas_perforadas).
sintoma(excremento_visible).
sintoma(puntos_amarillos).
sintoma(telarana_fina).
sintoma(manchas_necroticas).
sintoma(hojas_marchitas).
sintoma(polvo_blanco).

% causa(Causa, Tipo, SintomasQueLaCaracterizan)
causa(deficiencia_nitrogeno, deficiencia, [hojas_amarillas, hojas_viejas_primero, crecimiento_lento]).
causa(deficiencia_fosforo,   deficiencia, [hojas_moradas, crecimiento_lento]).
causa(deficiencia_potasio,   deficiencia, [bordes_quemados, hojas_viejas_primero]).
causa(deficiencia_hierro,    deficiencia, [hojas_amarillas, venas_verdes, hojas_nuevas_primero]).
causa(pulgones,              plaga,       [hojas_enrolladas, melaza_pegajosa]).
causa(mosca_blanca,          plaga,       [hojas_amarillas, melaza_pegajosa, insectos_blancos]).
causa(gusano_cogollero,      plaga,       [hojas_perforadas, excremento_visible]).
causa(arana_roja,            plaga,       [puntos_amarillos, telarana_fina]).
causa(tizon,                 enfermedad,  [manchas_necroticas, hojas_marchitas]).
causa(oidio,                 enfermedad,  [polvo_blanco, hojas_amarillas]).

% tratamiento(Causa, Accion)
tratamiento(deficiencia_nitrogeno, aplicar_fertilizante_nitrogenado).
tratamiento(deficiencia_fosforo,   aplicar_fertilizante_fosforado).
tratamiento(deficiencia_potasio,   aplicar_fertilizante_potasico).
tratamiento(deficiencia_hierro,    aplicar_hierro_y_revisar_ph).
tratamiento(pulgones,              controlar_plaga).
tratamiento(mosca_blanca,          controlar_plaga).
tratamiento(gusano_cogollero,      controlar_plaga).
tratamiento(arana_roja,            controlar_plaga).
tratamiento(tizon,                 controlar_hongos).
tratamiento(oidio,                 controlar_hongos).

% gravedad(Tipo, Severidad)
gravedad(deficiencia, media).
gravedad(plaga,       alta).
gravedad(enfermedad,  alta).

% ---------------------------------------------------------------------
% REGLAS: plagas, enfermedades y deficiencias
% ---------------------------------------------------------------------
% Una causa es probable si TODOS sus síntomas característicos fueron
% observados. Especificidad = cuántos síntomas la caracterizan (más
% síntomas coincidentes = diagnóstico más específico).
causa_probable(Sintomas, Causa, Tipo, Accion, Especificidad, Severidad) :-
    causa(Causa, Tipo, Requeridos),
    subset(Requeridos, Sintomas),
    length(Requeridos, Especificidad),
    tratamiento(Causa, Accion),
    gravedad(Tipo, Severidad).
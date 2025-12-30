--- detectar pacientes con mayor actividad sospechosa.
--- Cuántas ventanas sospechosas por paciente?
/*
SELECT
    patient_id,
    COUNT(*) AS suspected_windows
FROM eeg_seizure_events_db.eeg_window_events
WHERE suspected = true
GROUP BY patient_id
ORDER BY suspected_windows DESC;
*/




--- carga operativa diaria del sistema.
--- ¿Cuántas sesiones activas por día?
/*
SELECT
    DATE(substr(timestamp, 1, 10)) AS event_date,
    COUNT(DISTINCT session_id) AS active_sessions
FROM eeg_seizure_events_db.eeg_window_events
GROUP BY DATE(substr(timestamp, 1, 10))
ORDER BY event_date;



*/
--- análisis espacial / operativo por sala.
--- ¿En qué cuartos ocurre mayor frecuencia de eventos?
/*
SELECT
    room_id,
    COUNT(*) AS total_events,
    SUM(CASE WHEN suspected THEN 1 ELSE 0 END) AS suspected_events
FROM eeg_seizure_events_db.eeg_window_events
GROUP BY room_id
ORDER BY suspected_events DESC;
*/


--- Evolución temporal de scores sospechosos
--- detectar patrones temporales (pre-ictales).
/*
SELECT
    substr(timestamp, 1, 13) AS hour_bucket,
    AVG(score) AS avg_score,
    MAX(score) AS max_score
FROM eeg_seizure_events_db.eeg_window_events
WHERE suspected = true
GROUP BY substr(timestamp, 1, 13)
ORDER BY hour_bucket;
*/



--- Sesiones que superaron el umbral X de ventanas sospechosas
--- correlación con EDF subidos al bucket.
/*
SELECT
    patient_id,
    session_id,
    COUNT(*) AS suspected_windows
FROM eeg_seizure_events_db.eeg_window_events
WHERE suspected = true
GROUP BY patient_id, session_id
HAVING COUNT(*) >= 5
ORDER BY suspected_windows DESC;
*/


--- Score promedio por sesión (resumen clíSELECT
SELECT
    patient_id,
    session_id,
    AVG(score) AS avg_score,
    MAX(score) AS max_score
FROM eeg_seizure_events_db.eeg_window_events
GROUP BY patient_id, session_id
ORDER BY max_score DESC;


-- Each query starts with a "-- name:" line. 02_sql_analysis.py reads this file.

-- name: yearly_trend
SELECT crop, year,
       ROUND(SUM(area_ha), 0)      AS total_area_ha,
       ROUND(SUM(production_t), 0) AS total_production_t,
       ROUND(SUM(production_t) / SUM(area_ha), 2) AS yield_t_ha
FROM crop_production
GROUP BY crop, year
ORDER BY crop, year;

-- name: top_states
-- top 5 states for each crop by total production (window function RANK)
SELECT * FROM (
    SELECT crop, state,
           ROUND(SUM(production_t), 0) AS total_production_t,
           RANK() OVER (PARTITION BY crop ORDER BY SUM(production_t) DESC) AS rank_in_crop
    FROM crop_production
    GROUP BY crop, state
)
WHERE rank_in_crop <= 5
ORDER BY crop, rank_in_crop;

-- name: season_summary
SELECT crop, season,
       COUNT(*) AS records,
       ROUND(SUM(production_t), 0) AS total_production_t,
       ROUND(SUM(production_t) / SUM(area_ha), 2) AS yield_t_ha
FROM crop_production
GROUP BY crop, season
HAVING COUNT(*) >= 50
ORDER BY crop, total_production_t DESC;

-- name: state_share
-- share of each state in the national production of the crop
SELECT crop, state,
       ROUND(SUM(production_t), 0) AS total_production_t,
       ROUND(100.0 * SUM(production_t) / SUM(SUM(production_t)) OVER (PARTITION BY crop), 2) AS share_percent
FROM crop_production
GROUP BY crop, state
ORDER BY crop, share_percent DESC;

-- name: yield_growth
-- yield in the first 3 years (1998-2000) compared with the last 3 years (2012-2014)
WITH early AS (
    SELECT crop, state, SUM(production_t) / SUM(area_ha) AS early_yield
    FROM crop_production WHERE year BETWEEN 1998 AND 2000
    GROUP BY crop, state HAVING SUM(area_ha) > 10000
),
late AS (
    SELECT crop, state, SUM(production_t) / SUM(area_ha) AS late_yield
    FROM crop_production WHERE year BETWEEN 2012 AND 2014
    GROUP BY crop, state HAVING SUM(area_ha) > 10000
)
SELECT e.crop, e.state,
       ROUND(e.early_yield, 2) AS yield_1998_2000,
       ROUND(l.late_yield, 2)  AS yield_2012_2014,
       ROUND(100.0 * (l.late_yield - e.early_yield) / e.early_yield, 1) AS growth_percent
FROM early e JOIN late l ON e.crop = l.crop AND e.state = l.state
ORDER BY e.crop, growth_percent DESC;

-- name: best_yield_states
-- states with the highest average yield for each crop (only states with enough area)
SELECT * FROM (
    SELECT crop, state,
           ROUND(SUM(production_t) / SUM(area_ha), 2) AS yield_t_ha,
           ROUND(SUM(area_ha), 0) AS total_area_ha,
           RANK() OVER (PARTITION BY crop ORDER BY SUM(production_t) / SUM(area_ha) DESC) AS yield_rank
    FROM crop_production
    GROUP BY crop, state
    HAVING SUM(area_ha) > 100000
)
WHERE yield_rank <= 5
ORDER BY crop, yield_rank;

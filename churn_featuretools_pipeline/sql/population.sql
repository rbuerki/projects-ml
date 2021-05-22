DECLARE @earliest_jamo_for_grundgesamtheit INT = 201808;

-- Preselection of accounts
IF OBJECT_ID('tempdb.dbo.[#preselection_konto_lauf]') IS NOT NULL 
	DROP TABLE #preselection_konto_lauf
;

SELECT		KJ.konto_lauf_id
INTO		#preselection_konto_lauf
FROM		jemas_history.dbo.konto_jamo AS KJ
LEFT JOIN	jemas_base.dbo.konto_spezial_help AS KSH
	ON		KJ.konto_id = KSH.konto_id
WHERE		KJ.jamo >= @earliest_jamo_for_grundgesamtheit
AND			KJ.zustand_id = 1
AND			ISNULL(KSH.ist_technisch, 0) = 0
GROUP BY	KJ.konto_lauf_id
-- Some konto_lauf_id have multiple konto_id per jamo with zustand_id < 4. The following
-- HAVING clause excludes these -> Should not be a problem. From 201701 - 201904 this
-- drops only 117 konto_lauf_ids
HAVING		COUNT(*) = COUNT(DISTINCT jamo)
    --- Drops around 3 konto_lauf_ids which have one or more missing person_id entries
AND			COUNT(*) = COUNT(KJ.kontoinhaber_person_id);
;

IF OBJECT_ID('tempdb.dbo.[#konto_lauf_with_jamo]') IS NOT NULL
	DROP TABLE #konto_lauf_with_jamo
;

SELECT		DISTINCT
			PA.konto_lauf_id
			, KJ.jamo
INTO		#konto_lauf_with_jamo
FROM		#preselection_konto_lauf AS PA
JOIN		jemas_history.dbo.konto_jamo AS KJ
	ON		PA.konto_lauf_id = KJ.konto_lauf_id
    AND		KJ.jamo >= @earliest_jamo_for_grundgesamtheit
;

-- Due to the constraints imposed on #preselection_konto_lauf the following table
-- should be unique on konto_lauf_id and jamo -> this is tested after table creation
IF OBJECT_ID('tempdb.dbo.[#churn_population_full]') IS NOT NULL
	DROP TABLE #churn_population_full
;

SELECT		KLJ.konto_lauf_id
			, KLJ.jamo
			, KJ.konto_id
			, KJ.zustand_id
			, KJ.kontostatus_id
			, KJ.kontoinhaber_person_id
INTO		#churn_population_full
FROM		#konto_lauf_with_jamo AS KLJ
LEFT JOIN	jemas_history.dbo.konto_jamo AS KJ
	ON		KLJ.konto_lauf_id = KJ.konto_lauf_id
    AND		KLJ.jamo = KJ.jamo
    AND		KJ.zustand_id = 1
LEFT JOIN	jemas_base.dbo.konto_spezial_help AS KSH
    ON		KJ.konto_id = KSH.konto_id
WHERE		ISNULL(KSH.ist_technisch, 0) = 0
;


IF EXISTS (SELECT konto_lauf_id, jamo, COUNT(*)
           FROM #churn_population_full
           GROUP BY konto_lauf_id, jamo
           HAVING COUNT(*) > 1)
PRINT 'WARNING: See #churn_population_full'
;

---------------------------------------------------------------------------------------------------------------------------------
--	exclude bcag employees
---------------------------------------------------------------------------------------------------------------------------------
IF OBJECT_ID('tempdb.dbo.[#employees]') IS NOT NULL
	DROP TABLE #employees
;

with employee_bcag AS (
SELECT		DISTINCT 
			KI.person_id
FROM		jemas_base.dbo.Karteninhaber KI
JOIN		jemas_base.dbo.Gebuehrenset G ON G.gebuehrenset_id = KI.gebuehrenset_id
AND			bezeichung LIKE '%MITA%'
AND			bezeichung NOT LIKE '%SBB%' 
AND			bezeichung NOT LIKE '%partn%'
AND			bezeichung NOT LIKE '%TUI%'

UNION 

SELECT		person_id
FROM		jemas_base.dbo.Person
WHERE		personenstatus_id = 1 -- Mitarbeiter/-in BCAG
)

SELECT		emp.person_id
			, mki.konto_lauf_id
into		#employees
FROM		employee_bcag as emp
JOIN		jemas_dw.dbo.dd_master_karteninhaber AS mki
	ON		mki.person_id = emp.person_id
;

----------------------------------------------------------------------------------------
-- Remove jamos with no new information -> all features are the same as previous jamo
----------------------------------------------------------------------------------------
IF OBJECT_ID('tempdb.dbo.[#accounts]') IS NOT NULL DROP TABLE #accounts
;WITH prep AS (
SELECT		CP1.*
    -- Individual lines in case when statement evaluate to true if and only if either both columns are the same or both are NULL
    -- Therefore, new = 1 if any column changed its value with NULL being treated like any normal value, e.g. change from NULL -> some other value
    -- would set new = 1
			, new = CASE WHEN ((CP1.konto_id = CP2.konto_id) OR (ISNULL(CP1.konto_id, CP2.konto_id) IS NULL))
								AND ((CP1.zustand_id = CP2.zustand_id) OR (ISNULL(CP1.zustand_id, CP2.zustand_id) IS NULL))
								AND ((CP1.kontostatus_id = CP2.kontostatus_id) OR (ISNULL(CP1.kontostatus_id, CP2.kontostatus_id) IS NULL))
								AND ((CP1.kontoinhaber_person_id = CP2.kontoinhaber_person_id) OR (ISNULL(CP1.kontoinhaber_person_id, CP2.kontoinhaber_person_id) IS NULL))
					THEN 0 ELSE 1 END
			, rwn = ROW_NUMBER() OVER(PARTITION BY CP1.konto_lauf_id ORDER BY CP1.jamo)
FROM		#churn_population_full AS CP1
LEFT JOIN	#churn_population_full AS CP2
	ON		CP1.konto_lauf_id = CP2.konto_lauf_id
	AND		CASE WHEN CP2.jamo%100 = 12 THEN CP2.jamo+89 ELSE CP2.jamo+1 END = CP1.jamo
where		cp1.konto_lauf_id not in (select distinct konto_lauf_id from #employees)
)

SELECT		konto_lauf_id
			, konto_id
			, prep.jamo
			, j.letzter_tag
			, zustand_id
			, kontostatus_id
			, person_id = kontoinhaber_person_id
INTO		#accounts
FROM		prep
JOIN		jemas_dw.dbo.jamo AS j
	ON		j.jamo = prep.jamo
WHERE		rwn = 1
OR			new = 1
;

IF OBJECT_ID('jemas_temp.thm.churn21_population') IS NOT NULL DROP TABLE jemas_temp.thm.churn21_population
-- correct churn population for accounts that have not used their migrated/repositioned product
-- i.e., final kontostatus_id in (60, 61, 62, 63)
; with prep as (
SELECT		a.konto_lauf_id
			, a.konto_id
			, vkh.load_lauf_end_datum
			, vkh.kontostatus_id
			, rwn = ROW_NUMBER() OVER(PARTITION BY vkh.konto_id ORDER BY load_lauf_end_datum desc, datenstand_jecas_datum desc)
FROM		#accounts as a
LEFT JOIN	jemas_history.dbo.v_konto_history as vkh on vkh.konto_id = a.konto_id
where		vkh.kontostatus_id is not null
)

, accounts_exclude as (
SELECT		konto_lauf_id
			, konto_id
FROM		prep
where		rwn = 1
and			kontostatus_id in (60, 61, 62, 63)
)

SELECT		a.konto_lauf_id
			, a.konto_id
			, a.person_id
			, a.jamo
			, a.zustand_id
			, a.kontostatus_id
			, a.letzter_tag
into		jemas_temp.thm.churn21_population
FROM		#accounts as a
LEFT JOIN	accounts_exclude AS excl
	ON		excl.konto_lauf_id = a.konto_lauf_id
	AND		excl.konto_id = a.konto_id
where		(excl.konto_id is null) and (excl.konto_lauf_id is null)
;

IF EXISTS (
		SELECT		konto_lauf_id, jamo, count(*)
        FROM		jemas_temp.thm.churn21_population
        GROUP BY	konto_lauf_id, jamo
		having		count(*) > 1
		)
PRINT 'WARNING: See jemas_temp.thm.churn21_population'
;

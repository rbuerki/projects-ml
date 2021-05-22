IF OBJECT_ID('jemas_temp.thm.churn21_fakturadaten') IS NOT NULL 
	DROP TABLE jemas_temp.thm.churn21_fakturadaten
IF OBJECT_ID('tempdb.dbo.#prep_fd') IS NOT NULL 
	DROP TABLE tempdb.dbo.#prep_fd
;

declare @earliest_jamo_for_grundgesamtheit int = (select min(jamo) from jemas_temp.thm.churn21_population)
;

WITH		
prep_churn_population AS (
SELECT		DISTINCT 
			konto_lauf_id
			, konto_id
FROM		jemas_temp.thm.churn21_population
)

, fakturadaten AS (
SELECT		P.konto_lauf_id
			, P.konto_id
			, A.jamo
			, A.billingcycle_id
			, ISNULL(A.saldo_neu,0) AS saldo_neu
			, ISNULL(A.zahlungen,0) AS zahlungen
			, ISNULL(A.saldo_alt,0) AS saldo_alt
FROM		prep_churn_population AS P
JOIN		jemas_base.dbo.Fakturadaten A
	ON		P.konto_id = A.konto_id
    AND		A.jamo >= (select min(jamo) from jemas_temp.thm.churn21_population)
WHERE		A.abrechnungs_id NOT IN (SELECT abrechnungs_id FROM jemas_base.dbo.abrechnung_help WHERE lc = 1)
)

, slips as (
-- primary key on konto_id and abrechnungs_id
SELECT		fd.konto_lauf_id
			, fd.konto_id
			, fd.abrechnungs_id
			, fd.jamo
			, fd.erfassung_datum
			, fd.sind_zinsen_geschenkt
			, fd.ist_mahngebuehr_erlassen
FROM		prep_churn_population as acc
JOIN		jemas_base.dbo.Fakturadaten as fd 
	on		fd.konto_lauf_id = acc.konto_lauf_id
	and		fd.konto_id = acc.konto_id
WHERE		jamo >= @earliest_jamo_for_grundgesamtheit
AND			(sind_zinsen_geschenkt > 0 OR ist_mahngebuehr_erlassen > 0)
)


SELECT		fd.konto_lauf_id
			, fd.konto_id
			, fd.jamo
			, is_revolver = CASE WHEN fd.saldo_alt > 0 AND fd.zahlungen < fd.saldo_alt THEN 1 ELSE 0 END
			, ausstehend = fd.saldo_alt - fd.zahlungen
			, sind_zinsen_geschenkt = isnull(slips.sind_zinsen_geschenkt, 0)
			, ist_mahngebuehr_erlassen = isnull(slips.ist_mahngebuehr_erlassen, 0)
			, fd.billingcycle_id
INTO		#prep_fd
FROM		fakturadaten as fd
LEFT JOIN	slips 
	ON		slips.konto_id = fd.konto_id
	AND		slips.jamo = fd.jamo
;
IF OBJECT_ID('tempdb.dbo.#T') IS NOT NULL 
	DROP TABLE #T
;

SELECT		*
			, Pre_Grp = DENSE_RANK() OVER (PARTITION BY konto_lauf_id ORDER BY jamo) - DENSE_RANK() OVER (PARTITION BY konto_lauf_id, is_revolver ORDER BY jamo)
into		#T
FROM		#prep_fd
;

IF OBJECT_ID('tempdb.dbo.#MINIMUM') IS NOT NULL 
	DROP TABLE #MINIMUM
;

SELECT		konto_lauf_id
			, is_revolver
			, Pre_Grp
			, MIN_Seq = MIN(jamo)
INTO		#MINIMUM
FROM		#T
GROUP BY	konto_lauf_id
			, is_revolver
			, Pre_Grp
;

IF OBJECT_ID('tempdb.dbo.#GROUPS') IS NOT NULL 
	DROP TABLE #GROUPS
;

SELECT		T.*
			, Grp = DENSE_RANK() OVER (PARTITION BY T.konto_id ORDER BY M.MIN_Seq)
INTO		#GROUPS
FROM		#T AS T
JOIN		#MINIMUM as M
	ON		M.konto_lauf_id = T.konto_lauf_id 
	AND		M.is_revolver = T.is_revolver 
	AND		M.Pre_Grp = T.Pre_Grp
;


IF OBJECT_ID('tempdb.dbo.#results') IS NOT NULL 
	DROP TABLE #results
;
SELECT		*
			, revolve_cum = case when is_revolver = 1 then ROW_NUMBER() OVER(PARTITION BY konto_lauf_id, Grp ORDER BY jamo) else 0 end
into		#results
FROM		#groups
;

SELECT		konto_lauf_id
			, r.jamo
			, j.letzter_tag
			, is_revolver = max(is_revolver)
			, ausstehend = sum(ausstehend)
			, sind_zinsen_geschenkt = max(convert(int, sind_zinsen_geschenkt))
			, ist_mahngebuehr_erlassen = max(convert(int, ist_mahngebuehr_erlassen))
			, revolve_cum = max(revolve_cum)
into		jemas_temp.thm.churn21_fakturadaten
FROM		#results as r
JOIN		jemas_dw.dbo.jamo AS j
	ON		j.jamo = r.jamo
GROUP BY	konto_lauf_id
			, r.jamo
			, j.letzter_tag
;


IF EXISTS (SELECT konto_lauf_id, jamo, COUNT(*)
			FROM jemas_temp.thm.churn21_fakturadaten
			GROUP BY konto_lauf_id, jamo
			HAVING COUNT(*) > 1)
	PRINT 'WARNING: Duplicates in jemas_temp.thm.churn21_fakturadaten'
;

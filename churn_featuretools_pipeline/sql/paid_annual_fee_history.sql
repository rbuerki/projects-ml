IF OBJECT_ID('tempdb.dbo.[#accounts_relevant_for_jg]') IS NOT NULL 
		DROP TABLE #accounts_relevant_for_jg
;

SELECT		DISTINCT 
			konto_lauf_id
INTO		#accounts_relevant_for_jg
FROM		jemas_temp.thm.churn21_population
WHERE		konto_id IS NOT NULL
;

IF OBJECT_ID('jemas_temp.thm.churn21_annual_fee_history') IS NOT NULL 
		DROP TABLE jemas_temp.thm.churn21_annual_fee_history
;

SELECT		RA.konto_lauf_id
			, FF.jecas_bew_kopf_id
			, FF.jecas_bewdetail_nr
			, FF.referenz_jecas_bew_kopf_id
			, FF.betrag
			, FF.kauf_datum
			, FF.bewegungsgrund_id
			, FF.stornocode_id
INTO		jemas_temp.thm.churn21_annual_fee_history
FROM		#accounts_relevant_for_jg AS RA
JOIN		jemas_base.dbo.Fees_Fact AS FF
	ON		RA.konto_lauf_id = FF.konto_lauf_id
	AND		FF.stornocode_id = 1
	AND		(
				-- The restriction on betrag < 0 for JGR excludes around 8 weird observations
				(FF.bewegungsgrund_id = 'JGR' AND FF.betrag < 0 )
				OR (FF.bewegungsgrund_id IN ('JGT', 'JGE'))
			)
	and		ff.kauf_datum >= '2015-12-31'

IF EXISTS (SELECT jecas_bew_kopf_id, jecas_bewdetail_nr, COUNT(*)
			FROM jemas_temp.thm.churn21_annual_fee_history
			GROUP BY jecas_bew_kopf_id, jecas_bewdetail_nr
			HAVING COUNT(*) > 1)
	PRINT 'WARNING: Duplicates in jemas_temp.thm.churn21_annual_fee_history'
;

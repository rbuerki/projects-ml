----------------------------------------------------------------------------------------
-- Jahresgebühr
----------------------------------------------------------------------------------------
IF OBJECT_ID('tempdb.dbo.[#accounts_relevant_for_jg]') IS NOT NULL 
		DROP TABLE #accounts_relevant_for_jg
;

SELECT		DISTINCT 
			konto_lauf_id
			, konto_id
INTO		#accounts_relevant_for_jg
FROM		jemas_temp.thm.churn21_population
WHERE		konto_id IS NOT NULL

IF OBJECT_ID('jemas_temp.thm.churn21_annual_fee_date') IS NOT NULL
		 DROP TABLE jemas_temp.thm.churn21_annual_fee_date
;

-- Alle Daten der Jahresgebühr

SELECT		RA.konto_lauf_id
			, RA.konto_id
			, KIH.load_lauf_end_datum
			, KIH.jahresgebuehr_datum
			, KIH.inhaber_nr
			, is_hk_inhaber = CASE WHEN KJ.hk_inhaber_nr = KIH.inhaber_nr THEN 1 ELSE 0 END
INTO		jemas_temp.thm.churn21_annual_fee_date
FROM		#accounts_relevant_for_jg AS RA
JOIN		jemas_history.dbo.v_karteninhaber_history AS KIH
	ON		RA.konto_id = KIH.konto_id
JOIN		jemas_history.dbo.konto_jamo AS KJ
    ON		RA.konto_id = KJ.konto_id
    AND		YEAR(KIH.load_lauf_end_datum)*100+MONTH(KIH.load_lauf_end_datum) = KJ.jamo
WHERE		KIH.jahresgebuehr_datum IS NOT NULL
;


IF EXISTS (SELECT konto_lauf_id, konto_id, load_lauf_end_datum, inhaber_nr, COUNT(*)
           FROM jemas_temp.thm.churn21_annual_fee_date
           GROUP BY konto_lauf_id, konto_id, load_lauf_end_datum, inhaber_nr
           HAVING COUNT(*) > 1)
    PRINT 'WARNING: Duplicate records in jemas_temp.thm.churn21_annual_fee_date'
;

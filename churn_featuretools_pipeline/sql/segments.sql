
DECLARE @earliest_jamo_for_grundgesamtheit INT = (select MIN(jamo) from jemas_temp.thm.churn21_population)
;

-- The following table is unique by konto_lauf_id, jamo (verified after table creation)
IF OBJECT_ID('jemas_temp.thm.churn21_segments') IS NOT NULL 
	DROP TABLE jemas_temp.thm.churn21_segments
IF OBJECT_ID('tempdb.dbo.[#konto_lauf_id_jamo_info]') IS NOT NULL
	DROP TABLE #konto_lauf_id_jamo_info
IF OBJECT_ID('tempdb.dbo.#churn_pop') IS NOT NULL 
	DROP TABLE #churn_pop
IF OBJECT_ID('tempdb.dbo.#fmkj') IS NOT NULL 
	DROP TABLE #fmkj
;

SELECT		DISTINCT 
			konto_lauf_id
			, konto_id
into		#churn_pop
FROM		jemas_temp.thm.churn21_population
where		konto_id is not null
;


SELECT		prep.*
			, fmkj.jamo
			, fmkj.financial_profile_segment
			, fmkj.payment_type_segment
into		#fmkj
FROM		#churn_pop as prep
JOIN		if_core.calc.feature_market_konto_jamo AS fmkj
	ON		fmkj.konto_id = prep.konto_id
JOIN		jemas_history.dbo.konto_jamo AS kj
	ON		kj.konto_id = fmkj.konto_id
	AND		kj.jamo = fmkj.jamo
where		fmkj.financial_profile_segment is not null
and			kj.zustand_id = 1
;

IF OBJECT_ID('tempdb.dbo.#aff_cluster') IS NOT NULL 
	DROP TABLE #aff_cluster
;

SELECT		pop.*
			, acr.jamo
			, acr.cluster_name
into		#aff_cluster
FROM		#churn_pop as pop
JOIN		jemas_temp.thm.affinity_cluster_results AS acr
	ON		acr.konto_lauf_id = pop.konto_lauf_id
JOIN		jemas_history.dbo.konto_jamo AS kj
	ON		kj.konto_id = pop.konto_id
	AND		kj.jamo = acr.jamo
where		kj.zustand_id = 1
;

IF OBJECT_ID('tempdb.dbo.#segments') IS NOT NULL 
	DROP TABLE #segments
;

SELECT		fm.*
			, ac.cluster_name
into		#segments
FROM		#fmkj as fm
LEFT JOIN	#aff_cluster AS ac
	ON		ac.konto_lauf_id = fm.konto_lauf_id
	AND		ac.jamo = fm.jamo
ORDER BY	konto_lauf_id, jamo
;

with flag_new_ones as (
SELECT		s1.*
			, new = CASE WHEN ((s1.konto_id = s2.konto_id) OR (ISNULL(s1.konto_id, s2.konto_id) IS NULL)) and
							  ((s1.financial_profile_segment = s2.financial_profile_segment) or (isnull(s1.financial_profile_segment, s2.financial_profile_segment) is null)) and
							  ((s1.payment_type_segment = s2.payment_type_segment) or (isnull(s1.payment_type_segment, s2.payment_type_segment) is null)) and
							  ((s1.cluster_name = s2.cluster_name) or (isnull(s1.cluster_name, s2.cluster_name) is null))
							  then 0
							  else 1
					END
			, rwn = ROW_NUMBER() OVER(PARTITION BY s1.konto_lauf_id ORDER BY s1.jamo)
FROM		#segments as s1
LEFT JOIN	#segments AS s2
	ON		s2.konto_lauf_id = s1.konto_lauf_id
	AND		s2.jamo = case when s1.jamo % 100 = 12 then s1.jamo + 89 else s1.jamo + 1 end
)

SELECT		konto_lauf_id
			, f.jamo
			, j.letzter_tag
			, financial_profile_segment
			, payment_type_segment
			, cluster_name
into		jemas_temp.thm.churn21_segments
FROM		flag_new_ones as f
JOIN		jemas_dw.dbo.jamo AS j
	ON		j.jamo = f.jamo
where		new = 1
or			rwn = 1
;

if exists (
SELECT		konto_lauf_id
			, jamo
			, count(*)
FROM		jemas_temp.thm.churn21_segments
GROUP BY	konto_lauf_id
			, jamo
having		count(*) > 1
) PRINT 'WARNING: Duplicate records in jemas_temp.thm.churn21_segments'
;

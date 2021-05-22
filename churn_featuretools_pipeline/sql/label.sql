USE jemas_temp
;

IF OBJECT_ID('jemas_temp.thm.churn21_label') IS NOT NULL 
	DROP TABLE jemas_temp.thm.churn21_label
;


IF OBJECT_ID('tempdb.dbo.#konto_jamo') IS NOT NULL 
	DROP TABLE #konto_jamo
;


SELECT		distinct
			pop.konto_lauf_id
			, pop.letzter_tag
			, kj.konto_id
			, kj.jamo
			, kj.kontostatus_id
			, ks.kontostatus
			, kj.kuendigung_status_id
			, ksh.kuendigung_status
			, kj.kuendigung_an_datum
			, kj.kuendigung_auf_datum
			, kj.konversionsstatus_id
			, kvs.konversionsstatus
into		#konto_jamo
FROM		jemas_temp.thm.churn21_population as pop
JOIN		jemas_history.dbo.konto_jamo AS kj
	ON		kj.konto_lauf_id = pop.konto_lauf_id
	and		kj.jamo >= pop.jamo
JOIN		jemas_base.dbo.Kontostatus AS ks
	ON		ks.kontostatus_id = kj.kontostatus_id
JOIN		jemas_base.dbo.kuendigung_status_help AS ksh
	ON		ksh.kuendigung_status_id = kj.kuendigung_status_id
JOIN		jemas_base.dbo.Konversionsstatus AS kvs
	ON		kvs.konversionsstatus_id = kj.konversionsstatus_id
where		kj.kuendigung_an_datum is not null
and			kj.kuendigung_an_datum > pop.letzter_tag
--and			ksh.kuendigung_status_id in (1, 2, 3)
;

IF OBJECT_ID('tempdb.dbo.#konto_jamo_rwn') IS NOT NULL 
	DROP TABLE #konto_jamo_rwn 
;

SELECT		*
			, rwn = ROW_NUMBER() OVER(PARTITION BY konto_lauf_id, kuendigung_an_datum ORDER BY jamo desc)
into		#konto_jamo_rwn
FROM		#konto_jamo
;

with cancellation_type as (
SELECT		konto_lauf_id
			, kuendigung_status
			, kuendigung_an_datum
			, kuendigung_auf_datum
			, kontostatus_id
			, kuendigung_status_id
			, konversionsstatus_id
			, cancellation_type = case
										when kuendigung_an_datum < kuendigung_auf_datum and kontostatus_id in (11, 50, 51) then 'scheduled'
										when konversionsstatus_id between 86 and 89 or kuendigung_status_id = 2 then 'winback'
										when kontostatus_id in (50, 51) then 'not scheduled'
										when kontostatus_id not in (11, 50, 51) or kuendigung_status_id > 3 then 'other/irrelevant'
										else 'error'
								  end
FROM		#konto_jamo_rwn
where		rwn = 1
)


SELECT		*
into		jemas_temp.thm.churn21_label
FROM		cancellation_type
where		cancellation_type not in ('error', 'other/irrelevant')
;

-- checks

IF EXISTS (SELECT konto_lauf_id
           FROM jemas_temp.thm.churn21_label
           WHERE kuendigung_an_datum IS NULL)
    RAISERROR('See jemas_temp.churn21_label', 16, 1)

if exists (select * from (
				select konto_lauf_id, kuendigung_an_datum, n = COUNT(*)
				from jemas_temp.thm.churn21_label
				GROUP BY konto_lauf_id, kuendigung_an_datum
				) as a
			where n > 1
			)
	raiserror('duplicates in jemas_temp.churn21_label', 16, 1)
;
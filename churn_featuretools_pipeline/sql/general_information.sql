/*----------------------------------------------------------------------------------------
Assumptions:
----------------------
* If konto_lauf_id appears multiple times in a jamo (i.e. for multiple accounts) the kontoinhaber_person_id
  is the same -> for each jamo and konto_lauf_id there is a unique kontoinhaber_person_id
  Validated with:
	SELECT konto_lauf_id, jamo, COUNT(*), MAX(kontoinhaber_person_id), MIN(kontoinhaber_person_id)
	FROM jemas_history.dbo.konto_jamo
	WHERE jamo > 201801
		AND zustand_id < 4
	GROUP BY konto_lauf_id, jamo
	HAVING COUNT(*) > 1 AND MAX(kontoinhaber_person_id) <> MIN(kontoinhaber_person_id)
	-> results in no observations
----------------------------------------------------------------------------------------*/

DECLARE @earliest_jamo_for_grundgesamtheit INT = (select MIN(jamo) from jemas_temp.thm.churn21_population)
;

-- The following table is unique by konto_lauf_id, jamo (verified after table creation)
IF OBJECT_ID('tempdb.dbo.[#konto_lauf_id_jamo_info]') IS NOT NULL
	DROP TABLE #konto_lauf_id_jamo_info
;


WITH prep_churn_population AS (
    SELECT	DISTINCT 
			konto_lauf_id
    FROM	jemas_temp.thm.churn21_population
)

SELECT		KJ.konto_lauf_id
			, KJ.konto_id
			, KJ.jamo
			, person_id = KJ.kontoinhaber_person_id
			, KJ.produkt_id
			, KJ.hk_inhaber_nr
INTO		#konto_lauf_id_jamo_info
FROM		prep_churn_population AS CP
JOIN		jemas_history.dbo.konto_jamo AS KJ
	ON		CP.konto_lauf_id = KJ.konto_lauf_id
	AND		KJ.jamo >= @earliest_jamo_for_grundgesamtheit
	AND		KJ.zustand_id = 1
LEFT JOIN	jemas_base.dbo.konto_spezial_help AS KSH
	ON		KJ.konto_id = KSH.konto_id
WHERE		ISNULL(KSH.ist_technisch, 0) = 0
;


IF EXISTS (SELECT konto_lauf_id, jamo, COUNT(*)
			FROM #konto_lauf_id_jamo_info
			GROUP BY konto_lauf_id, jamo
			HAVING COUNT(*) > 1)
PRINT 'WARNING: valid konto_lauf_id duplicates per jamo in #konto_lauf_id_jamo_info'
;

----------------------------------------------------------------------------------------
-- Information on konto_id (jamo) level: VIP Status, Kreditlimite, survived repositioning, survived migration
----------------------------------------------------------------------------------------
IF OBJECT_ID('tempdb.dbo.[#account_info_included]') IS NOT NULL
	DROP TABLE #account_info_included
;


WITH account_migrated AS (
SELECT		distinct
			kh.konto_id
FROM		jemas_base.dbo.konto_help AS kh
LEFT JOIN	jemas_history.dbo.konto_jamo AS kj
	ON		kj.konto_id = kh.konto_id
	and		kj.jamo >= @earliest_jamo_for_grundgesamtheit
WHERE		kh.konto_id_alt IS NOT NULL
AND			kj.produkt_id IN (61, 62, 63)
)

, orig_vbc as (
SELECT		jamo
			, konto_id
			, produkt_id
FROM		jemas_history.dbo.konto_jamo
where		produkt_id in (2, 3)
and			jamo = 201602
and			zustand_id <= 3
)

, account_repositioned AS (
SELECT		DISTINCT 
			kj.konto_id
FROM		orig_vbc as o
LEFT JOIN	jemas_history.dbo.konto_jamo as kj
	ON		kj.konto_id = o.konto_id
	AND		kj.jamo > o.jamo
WHERE		kj.produkt_id IN (70, 71, 72, 85)
AND			kj.zustand_id <= 3
)

, account_jamo_kreditlimite AS (
SELECT		konto_id
			, jamo
			, kreditlimite
			, is_vip = case when kontokategorie_id_CA in (60, 65) then 1 else 0 end
FROM		jemas_history.dbo.kreditdaten_jamo
WHERE		jamo >= @earliest_jamo_for_grundgesamtheit
)

, account_jamo_herkunft_von_hk_inhaber AS (
-- konto_id, jamo is unique, however not if konto_id is replaced with konto_lauf_id
SELECT		konto_id
			, jamo
			, herkunft_id
FROM		jemas_history.dbo.karteninhaber_jamo
WHERE		ist_hk_inhaber = 1
AND			jamo >= @earliest_jamo_for_grundgesamtheit
)

SELECT		AC.konto_lauf_id
			, AC.jamo
			, AC.konto_id
			, AC.person_id
			, AC.produkt_id
			, kl.is_vip
			, is_migrated = CASE WHEN AM.konto_id IS NOT NULL THEN 1 ELSE 0 END
			, is_repositioned = CASE WHEN AR.konto_id IS NOT NULL THEN 1 ELSE 0 END
			, KL.kreditlimite
			, H.herkunft_id
INTO		#account_info_included
FROM		#konto_lauf_id_jamo_info AS AC
LEFT JOIN	account_migrated AS AM
	ON		AC.konto_id = AM.konto_id
LEFT JOIN	account_repositioned AS AR
	ON		AC.konto_id = AR.konto_id
LEFT JOIN	account_jamo_kreditlimite AS KL
	ON		AC.konto_id = KL.konto_id
	AND		AC.jamo = KL.jamo
LEFT JOIN	account_jamo_herkunft_von_hk_inhaber AS H
	ON		AC.konto_id = H.konto_id
	AND		AC.jamo = H.jamo
;

IF EXISTS (SELECT konto_lauf_id, jamo, COUNT(*)
			FROM #account_info_included
			GROUP BY konto_lauf_id, jamo
			HAVING COUNT(*) > 1)
	PRINT 'WARNING: See #account_info_included'
;

----------------------------------------------------------------------------------------
-- Information on person_id (jamo) level: Postal code, employee status, general_information / demographics
----------------------------------------------------------------------------------------
IF OBJECT_ID('tempdb.dbo.[#person_jamo_info_included]') IS NOT NULL 
		DROP TABLE #person_jamo_info_included
IF OBJECT_ID('tempdb..#plz_tmp') IS NOT NULL 
		DROP TABLE #plz_tmp
IF OBJECT_ID('tempdb..#tenure') IS NOT NULL 
		DROP TABLE #tenure
;

with plz_prep as (
SELECT		plz
			, n = count(*)
FROM		jemas_history.dbo.person_jamo
WHERE		jamo >= @earliest_jamo_for_grundgesamtheit
GROUP BY	plz
)

, plz_rwn as (
SELECT		*
			, rwn = ROW_NUMBER() OVER(ORDER BY n desc)
FROM		plz_prep
)

SELECT		plz
into		#plz_tmp
FROM		plz_rwn
where		rwn = 1
;

-- take min on erste_kundenbeziehung_datum and erfassung_datum (decided by heh and thm on 2021-04-22)
SELECT		pop.konto_lauf_id
			, dt_first_contact = min(case when p.erste_kundenbeziehung_datum < ko.erfassung_datum then p.erste_kundenbeziehung_datum else ko.erfassung_datum end)
into		#tenure
FROM		jemas_temp.thm.churn21_population as pop
JOIN		jemas_base.dbo.konto_help AS kh
	ON		pop.konto_id = kh.konto_id
JOIN		jemas_base.dbo.Konto AS ko
	ON		ko.konto_id = ISNULL(kh.konto_id_alt, kh.konto_id)
JOIN		jemas_base.dbo.person AS p
	ON		p.person_id = pop.person_id
GROUP BY	pop.konto_lauf_id
;

;WITH postal_code_per_jamo AS (
SELECT		person_id
			, jamo
			, plz = isnull(plz, (select plz from #plz_tmp))
FROM		jemas_history.dbo.person_jamo
WHERE		jamo >= @earliest_jamo_for_grundgesamtheit
)

, general_information AS (
SELECT		person_id
			, geburtsdatum
			, nationalitaet
			, sprachcode
			, berufsgruppe_id
			, anredecode
FROM		jemas_base.dbo.Person AS P
)


SELECT		AI.konto_lauf_id
			, AI.konto_id
			, AI.person_id
			, AI.jamo
			, AI.is_vip
			, AI.is_migrated
			, AI.is_repositioned
			, AI.kreditlimite
			, AI.herkunft_id
			, AI.produkt_id
			, postal_code = PC.plz
			, GI.geburtsdatum
			, GI.nationalitaet
			, GI.sprachcode
			, GI.berufsgruppe_id
			, GI.anredecode
			, t.dt_first_contact
INTO		#person_jamo_info_included
FROM		#account_info_included AS AI
LEFT JOIN	postal_code_per_jamo AS PC
	ON		AI.person_id = PC.person_id
	AND		AI.jamo = PC.jamo
LEFT JOIN	general_information AS GI
	ON		AI.person_id = GI.person_id
LEFT JOIN	#tenure AS t
	ON		t.konto_lauf_id = AI.konto_lauf_id
;

-- todo: segmente


IF EXISTS (SELECT konto_lauf_id, jamo
		   FROM #person_jamo_info_included
		   GROUP BY konto_lauf_id, jamo
		   HAVING COUNT(*) > 1)
PRINT 'WARNING: See #person_jamo_info_included'


----------------------------------------------------------------------------------------
-- Information on konto_lauf_id jamo level: Anzahl Karten
----------------------------------------------------------------------------------------
IF OBJECT_ID('tempdb.dbo.[#konto_lauf_jamo_info_included]') IS NOT NULL DROP TABLE #konto_lauf_jamo_info_included
;WITH anzahl_karten AS (
	SELECT konto_lauf_id
		, jamo
		, num_valid_cards = isnull(COUNT(*), 0)
	FROM jemas_history.dbo.karte_jamo
	WHERE zustand_id < 4
		AND jamo >= @earliest_jamo_for_grundgesamtheit
	GROUP BY konto_lauf_id, jamo
)

-- add whether account got first annual fee as a gift
, prep_jg_help as (
SELECT	konto_id
		, herkunft_id
FROM jemas_base.dbo.Konto
)

, jg_gift as (
SELECT	pjh.*
		, hk.herkunft
		, annual_fee_reduction = case when hk.herkunft like '%JG%' and hk.herkunft like '%1/1%' and
										   hk.herkunft like '%2 Jahr%' then 2
									  when hk.herkunft like '%JG%' and hk.herkunft like '%1/1%' then 1
									  when hk.herkunft like '%JG%' and hk.herkunft like '%1/2%' then .5
									  else 0
								 end
FROM prep_jg_help as pjh
left JOIN jemas_base.dbo.Herkunft as hk on hk.herkunft_id = pjh.herkunft_id
)

SELECT PJ.*
	, AK.num_valid_cards
    , jgg.annual_fee_reduction
INTO #konto_lauf_jamo_info_included
FROM #person_jamo_info_included AS PJ
	LEFT JOIN anzahl_karten AS AK
		ON PJ.konto_lauf_id = AK.konto_lauf_id
		AND PJ.jamo = AK.jamo
    LEFT JOIN jg_gift as jgg
		on PJ.konto_id = jgg.konto_id
;

IF EXISTS (SELECT konto_lauf_id, jamo
		   FROM #konto_lauf_jamo_info_included
		   GROUP BY konto_lauf_id, jamo
		   HAVING COUNT(*) > 1)
	PRINT 'WARNING: See #konto_lauf_jamo_info_included'
;

----------------------------------------------------------------------------------------
-- Remove jamos with no new information -> all features are the same as previous jamo
----------------------------------------------------------------------------------------
-- IF OBJECT_ID('tempdb.dbo.[#jamos_with_changes]') IS NOT NULL DROP TABLE #jamos_with_changes
IF OBJECT_ID('jemas_temp.thm.churn21_general_information') IS NOT NULL DROP TABLE jemas_temp.thm.churn21_general_information
;WITH prep AS (
    SELECT K1.*
        -- Individual lines in case when statement evaluate to true if and only if either both columns are the same or both are NULL
        -- Therefore, new = 1 if any column changed its value with NULL being treated like any normal value, e.g. change from NULL -> some other value
        -- would set new = 1
        , new = CASE WHEN ((K1.konto_id = K2.konto_id) OR (ISNULL(K1.konto_id, K2.konto_id) IS NULL))
							AND ((K1.person_id = K2.person_id) OR (ISNULL(K1.person_id, K2.person_id) IS NULL))
							AND ((K1.is_vip = K2.is_vip) OR (ISNULL(K1.is_vip, K2.is_vip) IS NULL))
							AND ((K1.is_migrated = K2.is_migrated) OR (ISNULL(K1.is_migrated, K2.is_migrated) IS NULL))
                            AND ((K1.is_repositioned = K2.is_repositioned) OR (ISNULL(K1.is_repositioned, K2.is_repositioned) IS NULL))
                            AND ((K1.kreditlimite = K2.kreditlimite) OR (ISNULL(K1.kreditlimite, K2.kreditlimite) IS NULL))
                            AND ((K1.herkunft_id = K2.herkunft_id) OR (ISNULL(K1.herkunft_id, K2.herkunft_id) IS NULL))
                            AND ((K1.produkt_id = K2.produkt_id) OR (ISNULL(K1.produkt_id, K2.produkt_id) IS NULL))
                            AND ((K1.postal_code = K2.postal_code) OR (ISNULL(K1.postal_code, K2.postal_code) IS NULL))
                            AND ((K1.geburtsdatum = K2.geburtsdatum) OR (ISNULL(K1.geburtsdatum, K2.geburtsdatum) IS NULL))
                            AND ((K1.nationalitaet = K2.nationalitaet) OR (ISNULL(K1.nationalitaet, K2.nationalitaet) IS NULL))
                            AND ((K1.sprachcode = K2.sprachcode) OR (ISNULL(K1.sprachcode, K2.sprachcode) IS NULL))
                            AND ((K1.berufsgruppe_id = K2.berufsgruppe_id) OR (ISNULL(K1.berufsgruppe_id, K2.berufsgruppe_id) IS NULL))
                            AND ((K1.anredecode = K2.anredecode) OR (ISNULL(K1.anredecode, K2.anredecode) IS NULL))
                            AND ((K1.dt_first_contact = K2.dt_first_contact) OR (ISNULL(K1.dt_first_contact, K2.dt_first_contact) IS NULL))
                            AND ((K1.num_valid_cards = K2.num_valid_cards) OR (ISNULL(K1.num_valid_cards, K2.num_valid_cards) IS NULL))
                            AND ((K1.annual_fee_reduction = K2.annual_fee_reduction) OR (ISNULL(K1.annual_fee_reduction, K2.annual_fee_reduction) IS NULL))
                THEN 0 ELSE 1 END
        , rwn = ROW_NUMBER() OVER(PARTITION BY K1.konto_lauf_id ORDER BY K1.jamo)
    FROM #konto_lauf_jamo_info_included AS K1
        LEFT JOIN #konto_lauf_jamo_info_included AS K2
            ON K1.konto_lauf_id = K2.konto_lauf_id
            AND CASE WHEN K2.jamo%100 = 12 THEN K2.jamo+89 ELSE K2.jamo+1 END = K1.jamo
)

, missing_dates as (
SELECT	m.konto_lauf_id
		, min_erfassung_datum = min(mk.erfassung_datum)
FROM prep as m
LEFT JOIN jemas_dw.dbo.dd_master_konto as mk on mk.konto_lauf_id = m.konto_lauf_id
GROUP BY m.konto_lauf_id
)

SELECT konto_lauf_id = GI.konto_lauf_id
		, person_id 
		, gi.jamo
		, j.letzter_tag
		, is_vip
		, is_migrated
		, is_repositioned
		, kreditlimite
		, herkunft_id
		, GI.produkt_id
		, is_prepaid = KT.ist_prepaid
		, postal_code
		, geburtsdatum
		, nationalitaet
		, sprachcode
		, berufsgruppe_id
		, anredecode
		, dt_first_contact = isnull(dt_first_contact, md.min_erfassung_datum)
		, num_valid_cards
        , annual_fee_reduction
INTO jemas_temp.thm.churn21_general_information
FROM prep AS GI
LEFT JOIN	jemas_base.dbo.Produkt AS P
	ON		GI.produkt_id = P.produkt_id
LEFT JOIN	jemas_base.dbo.Kartentyp AS KT
	ON		P.default_kartentyp_id = KT.kartentyp_id
JOIN		missing_dates as md
	on		md.konto_lauf_id = GI.konto_lauf_id
JOIN		jemas_dw.dbo.jamo AS j
	ON		j.jamo = gi.jamo
WHERE rwn = 1
    OR new = 1


IF EXISTS (SELECT konto_lauf_id, jamo
		   FROM jemas_temp.thm.churn21_general_information
		   GROUP BY konto_lauf_id, jamo
		   HAVING COUNT(*) > 1)
	PRINT 'WARNING: Duplicate records in jemas_temp.thm.churn21_general_information'


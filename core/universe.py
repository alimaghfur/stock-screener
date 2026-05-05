"""Curated ticker universes for IDX and US markets.

Lists are intentionally hand-maintained snapshots of the most liquid index members
so the app works fully offline (no scraping at runtime). Update them as needed; the
screener is agnostic to list size.

Sources of truth (refresh periodically):
- IDX30 / LQ45 / IDX80 / Kompas100 — idx.co.id quarterly evaluation announcements.
- JII / JII70 — idxislamic.idx.co.id; reviewed every 6 months (Mei & November).
- IDXBUMN20 / IDXHIDIV20 — idx.co.id; major evaluation every 6 months.
- IDX sectoral (IDXBASIC / IDXENERGY / IDXFINANCE / IDXTECHNO / etc) — derived from
  id.wikipedia.org listed-company table (IDX-IC classification). This is a SUPERSET
  of the official BEI sectoral indices because BEI applies additional free-float &
  liquidity filters; useful for thematic / rotation scanning across the full sector.
- IHSG / IDX Composite — full list of all BEI-listed tickers (~941). Heavy scan.
- S&P 500 / NASDAQ-100 / Dow 30 — en.wikipedia.org constituent tables (auto-maintained).
"""

from __future__ import annotations

# --- IDX (Indonesia Stock Exchange) ----------------------------------------------------
# Yahoo Finance suffix: ".JK"

IDX30: list[str] = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "TLKM.JK",
    "ASII.JK", "GOTO.JK", "ANTM.JK", "ADRO.JK", "PGAS.JK",
    "UNTR.JK", "SMGR.JK", "INDF.JK", "ICBP.JK", "KLBF.JK",
    "UNVR.JK", "INKP.JK", "MEDC.JK", "ITMG.JK", "PTBA.JK",
    "MNCN.JK", "EXCL.JK", "ISAT.JK", "CPIN.JK", "AMRT.JK",
    "ARTO.JK", "BRIS.JK", "MDKA.JK", "INCO.JK", "TPIA.JK",
]

LQ45: list[str] = sorted(set(IDX30 + [
    "BUKA.JK", "EMTK.JK", "ESSA.JK", "AKRA.JK", "BNGA.JK",
    "BTPS.JK", "HRUM.JK", "BSDE.JK", "CTRA.JK", "PWON.JK",
    "SMRA.JK", "ASRI.JK", "JPFA.JK", "TKIM.JK", "BRMS.JK",
]))

IDX80: list[str] = sorted(set(LQ45 + [
    "ADHI.JK", "ADMR.JK", "AGII.JK", "AMMN.JK", "ARCI.JK",
    "AUTO.JK", "AVIA.JK", "BBKP.JK", "BBTN.JK", "BFIN.JK",
    "BIRD.JK", "BJBR.JK", "BJTM.JK", "BNII.JK", "BRPT.JK",
    "CITA.JK", "DEWA.JK", "DOID.JK", "DSNG.JK", "ELSA.JK",
    "ENRG.JK", "ERAA.JK", "FILM.JK", "GGRM.JK", "HMSP.JK",
    "HRTA.JK", "IMAS.JK", "INDY.JK", "INTP.JK", "JSMR.JK",
    "LSIP.JK", "MAPI.JK", "MIKA.JK", "MTEL.JK", "NCKL.JK",
    "PANI.JK", "PNLF.JK", "RAJA.JK", "SCMA.JK", "SIDO.JK",
    "TBIG.JK", "TINS.JK", "TOWR.JK", "WIIM.JK", "WSKT.JK",
]))

# Kompas100 — broader IDX index of 100 most liquid + sizeable stocks. Snapshot below
# is sourced from id.wikipedia.org (Indeks_Kompas100) plus the Aug-Oct 2024 reshuffle
# announced by BEI; a few clearly delisted names from the Wikipedia snapshot have been
# removed (AISA, BUMI, BRAU, BTEL, BWPT, FAST, KBLV, MSKY, BHIT, STAR, TRAM).
KOMPAS100: list[str] = sorted(set([
    "AALI.JK", "ADMG.JK", "ADRO.JK", "AKRA.JK", "AMMN.JK", "ANTM.JK", "APIC.JK", "APLN.JK",
    "ASII.JK", "ASRI.JK", "AUTO.JK", "AVIA.JK", "BABP.JK", "BBCA.JK", "BBNI.JK", "BBRI.JK",
    "BBTN.JK", "BBYB.JK", "BDMN.JK", "BIRD.JK", "BISI.JK", "BJBR.JK", "BKSL.JK", "BMRI.JK",
    "BMTR.JK", "BNBR.JK", "BNGA.JK", "BRPT.JK", "BSDE.JK", "BULL.JK", "BYAN.JK", "CLPI.JK",
    "CMNP.JK", "CMRY.JK", "CPIN.JK", "CTRA.JK", "DEWA.JK", "DILD.JK", "ECII.JK", "ELSA.JK",
    "EMTK.JK", "EXCL.JK", "GIAA.JK", "GJTL.JK", "GOOD.JK", "HERO.JK", "HMSP.JK", "ICBP.JK",
    "IMAS.JK", "INCO.JK", "INDF.JK", "INDY.JK", "INKP.JK", "INTA.JK", "INTP.JK", "IPTV.JK",
    "ISAT.JK", "ITMG.JK", "JPFA.JK", "JPRS.JK", "JSMR.JK", "KIJA.JK", "KLBF.JK", "LPCK.JK",
    "LPKR.JK", "LPPF.JK", "LSIP.JK", "MAHA.JK", "MAPA.JK", "MAPB.JK", "MAPI.JK", "MLPL.JK",
    "MNCN.JK", "MPPA.JK", "MSIN.JK", "MYOR.JK", "NCKL.JK", "NETV.JK", "PANI.JK", "PJAA.JK",
    "PNBN.JK", "PNLF.JK", "PTBA.JK", "PTPP.JK", "PWON.JK", "ROTI.JK", "SCMA.JK", "SIDO.JK",
    "SIPD.JK", "SMCB.JK", "SMGR.JK", "SMRA.JK", "SSIA.JK", "TBIG.JK", "TINS.JK", "TLKM.JK",
    "ULTJ.JK", "UNSP.JK", "UNTR.JK", "UNVR.JK", "VKTR.JK",
]))

# JII — 30 saham syariah paling likuid (BEI Jakarta Islamic Index, Juni 2024).
JII: list[str] = [
    "ACES.JK", "ADMR.JK", "ADRO.JK", "AKRA.JK", "AMMN.JK", "ANTM.JK", "ASII.JK", "BRIS.JK",
    "BRMS.JK", "BRPT.JK", "CPIN.JK", "EXCL.JK", "GOTO.JK", "ICBP.JK", "INCO.JK", "INDF.JK",
    "INKP.JK", "ITMG.JK", "KLBF.JK", "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK", "PGAS.JK",
    "PGEO.JK", "PTBA.JK", "SMGR.JK", "TLKM.JK", "UNTR.JK", "UNVR.JK",
]

# JII70 — 70 saham syariah likuid (BEI Jakarta Islamic Index 70, Des 2023 - Mei 2024).
JII70: list[str] = [
    "ACES.JK", "ADMR.JK", "ADRO.JK", "AKRA.JK", "ANTM.JK", "ASII.JK", "AUTO.JK", "AVIA.JK",
    "BMTR.JK", "BRIS.JK", "BRMS.JK", "BSDE.JK", "BTPS.JK", "CMRY.JK", "CPIN.JK", "CTRA.JK",
    "DSNG.JK", "ELSA.JK", "EMTK.JK", "ENRG.JK", "ERAA.JK", "ESSA.JK", "EXCL.JK", "FILM.JK",
    "GOTO.JK", "HEAL.JK", "HRUM.JK", "ICBP.JK", "INCO.JK", "INDF.JK", "INDY.JK", "INKP.JK",
    "INTP.JK", "ISAT.JK", "ITMG.JK", "JPFA.JK", "KLBF.JK", "LPPF.JK", "MAPA.JK", "MAPI.JK",
    "MBMA.JK", "MDKA.JK", "MIKA.JK", "MNCN.JK", "MPMX.JK", "MTEL.JK", "MYOR.JK", "NCKL.JK",
    "NICL.JK", "PGAS.JK", "PGEO.JK", "PTBA.JK", "PTMP.JK", "PTPP.JK", "PWON.JK", "SCMA.JK",
    "SIDO.JK", "SMGR.JK", "SMRA.JK", "SMSM.JK", "SRTG.JK", "SSIA.JK", "SSMS.JK", "TINS.JK",
    "TKIM.JK", "TLKM.JK", "TPIA.JK", "UNTR.JK", "UNVR.JK", "WIFI.JK",
]

# IDXBUMN20 — 20 saham BUMN dengan likuiditas & kapitalisasi terbesar (BEI, Feb 2024).
IDXBUMN20: list[str] = [
    "ADHI.JK", "AGRO.JK", "ANTM.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", "BJBR.JK", "BJTM.JK",
    "BMRI.JK", "BRIS.JK", "ELSA.JK", "JSMR.JK", "MTEL.JK", "PGAS.JK", "PGEO.JK", "PTBA.JK",
    "PTPP.JK", "SMGR.JK", "TINS.JK", "TLKM.JK",
]

# IDXHIDIV20 — 20 saham high dividend yield (BEI, periode Feb 2025 - Feb 2026).
IDXHIDIV20: list[str] = [
    "ACES.JK", "ADRO.JK", "AKRA.JK", "ANTM.JK", "ASII.JK", "BBCA.JK", "BBNI.JK", "BBRI.JK",
    "BMRI.JK", "BNGA.JK", "HMSP.JK", "INDF.JK", "ITMG.JK", "JPFA.JK", "PGAS.JK", "PTBA.JK",
    "SIDO.JK", "TLKM.JK", "UNTR.JK", "UNVR.JK",
]

# IDX-IC sektoral indeks — semua saham yang tercatat di BEI dikelompokkan per sektor
# berdasarkan klasifikasi IDX Industrial Classification (id.wikipedia.org snapshot).
# Catatan: list ini superset dari indeks sektoral resmi BEI (yang menerapkan filter
# free-float & likuiditas), berguna untuk thematic/rotation scanning.
IDXBASIC: list[str] = [
    "ADMG.JK", "AGII.JK", "AKPI.JK", "ALDO.JK", "ALKA.JK", "ALMI.JK", "AMMN.JK", "ANTM.JK",
    "APLI.JK", "ARCI.JK", "AVIA.JK", "AYLS.JK", "BAJA.JK", "BATR.JK", "BEBS.JK", "BLES.JK",
    "BMSR.JK", "BRMS.JK", "BRNA.JK", "BRPT.JK", "BTON.JK", "CHEM.JK", "CITA.JK", "CLPI.JK",
    "CMNT.JK", "CTBN.JK", "DAAZ.JK", "DKFT.JK", "DPNS.JK", "EKAD.JK", "EPAC.JK", "ESIP.JK",
    "ESSA.JK", "ETWA.JK", "FASW.JK", "FPNI.JK", "FWCT.JK", "GDST.JK", "GGRP.JK", "HKMU.JK",
    "IFII.JK", "IFSH.JK", "IGAR.JK", "INAI.JK", "INCF.JK", "INCI.JK", "INCO.JK", "INKP.JK",
    "INRU.JK", "INTD.JK", "INTP.JK", "IPOL.JK", "ISSP.JK", "JKSW.JK", "KAYU.JK", "KBRI.JK",
    "KDSI.JK", "KKES.JK", "KMTR.JK", "KRAS.JK", "LMSH.JK", "LTLS.JK", "MBMA.JK", "MDKA.JK",
    "MDKI.JK", "MOLI.JK", "NCKL.JK", "NICE.JK", "NICL.JK", "NIKL.JK", "NPGF.JK", "OBMD.JK",
    "OKAS.JK", "OPMS.JK", "PACK.JK", "PBID.JK", "PDPP.JK", "PICO.JK", "PPRI.JK", "PSAB.JK",
    "PTMR.JK", "PURE.JK", "SAMF.JK", "SBMA.JK", "SIMA.JK", "SMBR.JK", "SMCB.JK", "SMGA.JK",
    "SMGR.JK", "SMKL.JK", "SMLE.JK", "SOLA.JK", "SPMA.JK", "SQMI.JK", "SRSN.JK", "SULI.JK",
    "SWAT.JK", "TALF.JK", "TBMS.JK", "TDPM.JK", "TINS.JK", "TIRT.JK", "TKIM.JK", "TPIA.JK",
    "TRST.JK", "UNIC.JK", "WSBP.JK", "WTON.JK", "YPAS.JK", "ZINC.JK",
]

IDXCYCLIC: list[str] = [
    "ABBA.JK", "ACES.JK", "ACRO.JK", "AEGS.JK", "AKKU.JK", "ARGO.JK", "ARTA.JK", "ASLC.JK",
    "AUTO.JK", "BABY.JK", "BAIK.JK", "BATA.JK", "BAUT.JK", "BAYU.JK", "BELL.JK", "BIKE.JK",
    "BIMA.JK", "BLTZ.JK", "BMBL.JK", "BMTR.JK", "BOGA.JK", "BOLA.JK", "BOLT.JK", "BRAM.JK",
    "BUVA.JK", "CARS.JK", "CBMF.JK", "CINT.JK", "CLAY.JK", "CNMA.JK", "CNTX.JK", "CSAP.JK",
    "CSMI.JK", "DEPO.JK", "DFAM.JK", "DIGI.JK", "DOOH.JK", "DOSS.JK", "DRMA.JK", "DUCK.JK",
    "EAST.JK", "ECII.JK", "ENAK.JK", "ERAA.JK", "ERAL.JK", "ERTX.JK", "ESTA.JK", "ESTI.JK",
    "FAST.JK", "FILM.JK", "FITT.JK", "FORU.JK", "FUTR.JK", "GDYR.JK", "GEMA.JK", "GJTL.JK",
    "GLOB.JK", "GOLF.JK", "GRPH.JK", "GWSA.JK", "HAJJ.JK", "HDTX.JK", "HOME.JK", "HOTL.JK",
    "HRME.JK", "HRTA.JK", "IDEA.JK", "IIKP.JK", "IMAS.JK", "INDR.JK", "INDS.JK", "INOV.JK",
    "IPTV.JK", "ISAP.JK", "JGLE.JK", "JIHD.JK", "JSPT.JK", "KDTN.JK", "KICI.JK", "KLIN.JK",
    "KOTA.JK", "KPIG.JK", "LFLO.JK", "LIVE.JK", "LMAX.JK", "LMPI.JK", "LPIN.JK", "LPPF.JK",
    "LUCY.JK", "MABA.JK", "MAMI.JK", "MAPA.JK", "MAPB.JK", "MAPI.JK", "MARI.JK", "MASA.JK",
    "MDIA.JK", "MEJA.JK", "MGLV.JK", "MGNA.JK", "MICE.JK", "MINA.JK", "MKNT.JK", "MNCN.JK",
    "MPMX.JK", "MSIN.JK", "MSKY.JK", "MYTX.JK", "NATO.JK", "NETV.JK", "NIPS.JK", "NUSA.JK",
    "OLIV.JK", "PANR.JK", "PART.JK", "PBRX.JK", "PDES.JK", "PGLI.JK", "PJAA.JK", "PLAN.JK",
    "PMJS.JK", "PNSE.JK", "POLU.JK", "POLY.JK", "PRAS.JK", "PSKT.JK", "PTSP.JK", "PZZA.JK",
    "RAAM.JK", "RAFI.JK", "RALS.JK", "RICY.JK", "SBAT.JK", "SCMA.JK", "SCNP.JK", "SHID.JK",
    "SLIS.JK", "SMSM.JK", "SNLK.JK", "SOFA.JK", "SONA.JK", "SOTS.JK", "SPRE.JK", "SRIL.JK",
    "SSTM.JK", "SWID.JK", "TELE.JK", "TFCO.JK", "TMPO.JK", "TOOL.JK", "TOYS.JK", "TRIO.JK",
    "TRIS.JK", "TYRE.JK", "UFOE.JK", "UNIT.JK", "UNTD.JK", "VERN.JK", "VIVA.JK", "VKTR.JK",
    "WOOD.JK", "YELO.JK", "ZATA.JK", "ZONE.JK",
]

IDXNONCYC: list[str] = [
    "AALI.JK", "ADES.JK", "AGAR.JK", "AISA.JK", "ALTO.JK", "AMMS.JK", "AMRT.JK", "ANDI.JK",
    "ANJT.JK", "ASHA.JK", "AYAM.JK", "BEEF.JK", "BEER.JK", "BISI.JK", "BOBA.JK", "BTEK.JK",
    "BUAH.JK", "BUDI.JK", "BWPT.JK", "CAMP.JK", "CBUT.JK", "CEKA.JK", "CLEO.JK", "CMRY.JK",
    "COCO.JK", "CPIN.JK", "CPRO.JK", "CRAB.JK", "CSRA.JK", "DAYA.JK", "DEWI.JK", "DLTA.JK",
    "DMND.JK", "DPUM.JK", "DSFI.JK", "DSNG.JK", "ENZO.JK", "EPMT.JK", "EURO.JK", "FAPA.JK",
    "FISH.JK", "FLMC.JK", "FOOD.JK", "GGRM.JK", "GOLL.JK", "GOOD.JK", "GRPM.JK", "GULA.JK",
    "GUNA.JK", "GZCO.JK", "HERO.JK", "HMSP.JK", "HOKI.JK", "IBOS.JK", "ICBP.JK", "IKAN.JK",
    "INDF.JK", "IPPE.JK", "ISEA.JK", "ITIC.JK", "JARR.JK", "JAWA.JK", "JPFA.JK", "KEJU.JK",
    "KINO.JK", "KMDS.JK", "KPAS.JK", "LAPD.JK", "LSIP.JK", "MAGP.JK", "MAIN.JK", "MAXI.JK",
    "MBTO.JK", "MGRO.JK", "MIDI.JK", "MKTR.JK", "MLBI.JK", "MLPL.JK", "MPPA.JK", "MRAT.JK",
    "MSJA.JK", "MYOR.JK", "NANO.JK", "NASI.JK", "NAYZ.JK", "NEST.JK", "NSSS.JK", "OILS.JK",
    "PCAR.JK", "PGUN.JK", "PMMP.JK", "PNGO.JK", "PSDN.JK", "PSGO.JK", "PTPS.JK", "RANC.JK",
    "ROTI.JK", "SDPC.JK", "SGRO.JK", "SIMP.JK", "SIPD.JK", "SKBM.JK", "SKLT.JK", "SMAR.JK",
    "SOUL.JK", "SSMS.JK", "STAA.JK", "STRK.JK", "STTP.JK", "TAPG.JK", "TAYS.JK", "TBLA.JK",
    "TCID.JK", "TGKA.JK", "TGUK.JK", "TLDN.JK", "TRGU.JK", "UCID.JK", "UDNG.JK", "ULTJ.JK",
    "UNSP.JK", "UNVR.JK", "VICI.JK", "WAPO.JK", "WICO.JK", "WIIM.JK", "WINE.JK", "WMPP.JK",
    "WMUU.JK",
]

IDXENERGY: list[str] = [
    "ABMM.JK", "ADMR.JK", "ADRO.JK", "AIMS.JK", "AKRA.JK", "ALII.JK", "APEX.JK", "ARII.JK",
    "ARTI.JK", "ATLA.JK", "BBRM.JK", "BESS.JK", "BIPI.JK", "BOAT.JK", "BOSS.JK", "BSML.JK",
    "BSSR.JK", "BULL.JK", "BUMI.JK", "BYAN.JK", "CANI.JK", "CBRE.JK", "CGAS.JK", "CNKO.JK",
    "COAL.JK", "CUAN.JK", "DEWA.JK", "DOID.JK", "DSSA.JK", "DWGL.JK", "ELSA.JK", "ENRG.JK",
    "FIRE.JK", "GEMS.JK", "GTBO.JK", "GTSI.JK", "HILL.JK", "HITS.JK", "HRUM.JK", "HUMI.JK",
    "IATA.JK", "INDY.JK", "INPS.JK", "ITMA.JK", "ITMG.JK", "JSKY.JK", "KKGI.JK", "KOPI.JK",
    "LEAD.JK", "MAHA.JK", "MBAP.JK", "MBSS.JK", "MCOL.JK", "MEDC.JK", "MKAP.JK", "MTFN.JK",
    "MYOH.JK", "PGAS.JK", "PKPK.JK", "PSSI.JK", "PTBA.JK", "PTIS.JK", "PTRO.JK", "RAJA.JK",
    "RGAS.JK", "RIGS.JK", "RMKE.JK", "RMKO.JK", "RUIS.JK", "SEMA.JK", "SGER.JK", "SHIP.JK",
    "SICO.JK", "SMMT.JK", "SMRU.JK", "SOCI.JK", "SUGI.JK", "SUNI.JK", "SURE.JK", "TAMU.JK",
    "TCPI.JK", "TEBE.JK", "TOBA.JK", "TPMA.JK", "TRAM.JK", "UNIQ.JK", "WINS.JK", "WOWS.JK",
]

IDXFINANCE: list[str] = [
    "ABDA.JK", "ADMF.JK", "AGRO.JK", "AGRS.JK", "AHAP.JK", "AMAG.JK", "AMAR.JK", "AMOR.JK",
    "APIC.JK", "ARTO.JK", "ASBI.JK", "ASDM.JK", "ASJT.JK", "ASMI.JK", "ASRM.JK", "BABP.JK",
    "BACA.JK", "BANK.JK", "BBCA.JK", "BBHI.JK", "BBKP.JK", "BBLD.JK", "BBMD.JK", "BBNI.JK",
    "BBRI.JK", "BBSI.JK", "BBTN.JK", "BBYB.JK", "BCAP.JK", "BCIC.JK", "BDMN.JK", "BEKS.JK",
    "BFIN.JK", "BGTG.JK", "BHAT.JK", "BINA.JK", "BJBR.JK", "BJTM.JK", "BKSW.JK", "BMAS.JK",
    "BMRI.JK", "BNBA.JK", "BNGA.JK", "BNII.JK", "BNLI.JK", "BPFI.JK", "BPII.JK", "BRIS.JK",
    "BSIM.JK", "BSWD.JK", "BTPN.JK", "BTPS.JK", "BVIC.JK", "CASA.JK", "CFIN.JK", "DEFI.JK",
    "DNAR.JK", "DNET.JK", "FUJI.JK", "GSMF.JK", "HDFA.JK", "INPC.JK", "JMAS.JK", "LIFE.JK",
    "LPGI.JK", "LPPS.JK", "MASB.JK", "MAYA.JK", "MCOR.JK", "MEGA.JK", "MFIN.JK", "MREI.JK",
    "MTWI.JK", "NICK.JK", "NISP.JK", "NOBU.JK", "OCAP.JK", "PADI.JK", "PALM.JK", "PANS.JK",
    "PEGE.JK", "PLAS.JK", "PNBN.JK", "PNBS.JK", "PNIN.JK", "PNLF.JK", "POLA.JK", "POOL.JK",
    "RELI.JK", "SDRA.JK", "SFAN.JK", "SMMA.JK", "SRTG.JK", "STAR.JK", "TIFA.JK", "TRIM.JK",
    "TRUS.JK", "TUGU.JK", "VICO.JK", "VINS.JK", "VRNA.JK", "VTNY.JK", "WOMF.JK", "YULE.JK",
]

IDXHEALTH: list[str] = [
    "BMHS.JK", "CARE.JK", "DGNS.JK", "DVLA.JK", "HALO.JK", "HEAL.JK", "IKPM.JK", "INAF.JK",
    "IRRA.JK", "KAEF.JK", "KLBF.JK", "LABS.JK", "MEDS.JK", "MERK.JK", "MIKA.JK", "MMIX.JK",
    "MTMH.JK", "OMED.JK", "PEHA.JK", "PEVE.JK", "PRAY.JK", "PRDA.JK", "PRIM.JK", "PYFA.JK",
    "RSCH.JK", "RSGK.JK", "SAME.JK", "SCPI.JK", "SIDO.JK", "SILO.JK", "SOHO.JK", "SRAJ.JK",
    "SURI.JK", "TSPC.JK",
]

IDXINDUST: list[str] = [
    "AMFG.JK", "AMIN.JK", "APII.JK", "ARKA.JK", "ARNA.JK", "ASGR.JK", "ASII.JK", "BHIT.JK",
    "BINO.JK", "BLUE.JK", "BNBR.JK", "CAKK.JK", "CCSI.JK", "CRSN.JK", "CTTH.JK", "DYAN.JK",
    "FOLK.JK", "GPSO.JK", "HEXA.JK", "HOPE.JK", "HYGN.JK", "IBFN.JK", "ICON.JK", "IKAI.JK",
    "IKBI.JK", "IMPC.JK", "INDX.JK", "INTA.JK", "JECC.JK", "JTPE.JK", "KBLI.JK", "KBLM.JK",
    "KIAS.JK", "KING.JK", "KOBX.JK", "KOIN.JK", "KONI.JK", "KPAL.JK", "KRAH.JK", "KUAS.JK",
    "LABA.JK", "LION.JK", "MARK.JK", "MDRN.JK", "MFMI.JK", "MHKI.JK", "MLIA.JK", "MUTU.JK",
    "NAIK.JK", "NTBK.JK", "PADA.JK", "PIPA.JK", "PTMP.JK", "SCCO.JK", "SINI.JK", "SKRN.JK",
    "SMIL.JK", "SOSS.JK", "SPTO.JK", "TIRA.JK", "TOTO.JK", "TRIL.JK", "UNTR.JK", "VISI.JK",
    "VOKS.JK", "WIDI.JK", "ZBRA.JK",
]

IDXINFRA: list[str] = [
    "ACST.JK", "ADHI.JK", "ARKO.JK", "ASLI.JK", "BALI.JK", "BDKR.JK", "BREN.JK", "BTEL.JK",
    "BUKK.JK", "CASS.JK", "CENT.JK", "CMNP.JK", "DATA.JK", "DGIK.JK", "EXCL.JK", "FIMP.JK",
    "FREN.JK", "GHON.JK", "GMFI.JK", "GOLD.JK", "HADE.JK", "IBST.JK", "IDPR.JK", "INET.JK",
    "IPCC.JK", "IPCM.JK", "ISAT.JK", "JAST.JK", "JKON.JK", "JSMR.JK", "KARW.JK", "KBLV.JK",
    "KEEN.JK", "KETR.JK", "KOKA.JK", "KRYA.JK", "LCKM.JK", "LINK.JK", "MANG.JK", "META.JK",
    "MORA.JK", "MPOW.JK", "MTEL.JK", "MTPS.JK", "MTRA.JK", "NRCA.JK", "OASA.JK", "PBSA.JK",
    "PGEO.JK", "PORT.JK", "POWR.JK", "PPRE.JK", "PTDU.JK", "PTPP.JK", "PTPW.JK", "RONY.JK",
    "SMKM.JK", "SSIA.JK", "SUPR.JK", "TAMA.JK", "TBIG.JK", "TGRA.JK", "TLKM.JK", "TOPS.JK",
    "TOTL.JK", "TOWR.JK", "WEGE.JK", "WIKA.JK", "WSKT.JK",
]

IDXPROPERT: list[str] = [
    "ADCP.JK", "AMAN.JK", "APLN.JK", "ARMY.JK", "ASPI.JK", "ASRI.JK", "ATAP.JK", "BAPA.JK",
    "BAPI.JK", "BBSS.JK", "BCIP.JK", "BEST.JK", "BIKA.JK", "BIPP.JK", "BKDP.JK", "BKSL.JK",
    "BSBK.JK", "BSDE.JK", "CBPE.JK", "CITY.JK", "COWL.JK", "CPRI.JK", "CSIS.JK", "CTRA.JK",
    "DADA.JK", "DART.JK", "DILD.JK", "DMAS.JK", "DUTI.JK", "ELTY.JK", "EMDE.JK", "FMII.JK",
    "FORZ.JK", "GAMA.JK", "GMTD.JK", "GPRA.JK", "GRIA.JK", "HBAT.JK", "HOMI.JK", "INDO.JK",
    "INPP.JK", "IPAC.JK", "JRPT.JK", "KBAG.JK", "KIJA.JK", "KOCI.JK", "LAND.JK", "LCGP.JK",
    "LPCK.JK", "LPKR.JK", "LPLI.JK", "MDLN.JK", "MKPI.JK", "MMLP.JK", "MPRO.JK", "MSIE.JK",
    "MTLA.JK", "MTSM.JK", "MYRX.JK", "NASA.JK", "NIRO.JK", "NZIA.JK", "OMRE.JK", "PAMG.JK",
    "PANI.JK", "PLIN.JK", "POLI.JK", "POLL.JK", "POSA.JK", "PPRO.JK", "PUDP.JK", "PURI.JK",
    "PWON.JK", "RBMS.JK", "RDTX.JK", "REAL.JK", "RELF.JK", "RIMO.JK", "RISE.JK", "ROCK.JK",
    "RODA.JK", "SAGE.JK", "SATU.JK", "SMDM.JK", "SMRA.JK", "TARA.JK", "TRIN.JK", "TRUE.JK",
    "UANG.JK", "URBN.JK", "VAST.JK", "WINR.JK",
]

IDXTECHNO: list[str] = [
    "AREA.JK", "ATIC.JK", "AWAN.JK", "AXIO.JK", "BELI.JK", "BUKA.JK", "CASH.JK", "CHIP.JK",
    "CYBR.JK", "DCII.JK", "DIVA.JK", "DMMX.JK", "EDGE.JK", "ELIT.JK", "EMTK.JK", "ENVY.JK",
    "GLVA.JK", "GOTO.JK", "HDIT.JK", "IOTF.JK", "IRSX.JK", "JATI.JK", "KIOS.JK", "KREN.JK",
    "LMAS.JK", "LUCK.JK", "MCAS.JK", "MENN.JK", "MLPT.JK", "MPIX.JK", "MSTI.JK", "MTDL.JK",
    "NFCX.JK", "NINE.JK", "PGJO.JK", "PTSN.JK", "RUNS.JK", "SKYB.JK", "TECH.JK", "TFAS.JK",
    "TOSK.JK", "TRON.JK", "UVCR.JK", "WGSH.JK", "WIFI.JK", "WIRG.JK", "ZYRX.JK",
]

IDXTRANS: list[str] = [
    "AKSI.JK", "ASSA.JK", "BIRD.JK", "BLTA.JK", "BPTR.JK", "CMPP.JK", "DEAL.JK", "ELPI.JK",
    "GIAA.JK", "GTRA.JK", "HAIS.JK", "HATM.JK", "HELI.JK", "IMJS.JK", "JAYA.JK", "KJEN.JK",
    "KLAS.JK", "LAJU.JK", "LOPI.JK", "LRNA.JK", "MIRA.JK", "MITI.JK", "MPXL.JK", "NELY.JK",
    "PPGL.JK", "PURA.JK", "RCCC.JK", "SAFE.JK", "SAPX.JK", "SDMU.JK", "SMDR.JK", "TAXI.JK",
    "TMAS.JK", "TNCA.JK", "TRJA.JK", "TRUK.JK", "WEHA.JK",
]

# IHSG / IDX Composite — full list dari semua saham yang tercatat di BEI (~941 emiten).
# Sumber: id.wikipedia.org/wiki/Daftar_perusahaan_yang_tercatat_di_Bursa_Efek_Indonesia.
# Snapshot 2025 — perlu refresh manual karena IPO/delist berubah tiap minggu.
# WARNING: scan IHSG (~941 ticker) bisa makan 10-15 menit. Banyak saham di list ini
# punya likuiditas sangat tipis dan tidak realistic untuk scalping/swing.
IHSG: list[str] = [
    "AALI.JK", "ABBA.JK", "ABDA.JK", "ABMM.JK", "ACES.JK", "ACRO.JK", "ACST.JK", "ADCP.JK",
    "ADES.JK", "ADHI.JK", "ADMF.JK", "ADMG.JK", "ADMR.JK", "ADRO.JK", "AEGS.JK", "AGAR.JK",
    "AGII.JK", "AGRO.JK", "AGRS.JK", "AHAP.JK", "AIMS.JK", "AISA.JK", "AKKU.JK", "AKPI.JK",
    "AKRA.JK", "AKSI.JK", "ALDO.JK", "ALII.JK", "ALKA.JK", "ALMI.JK", "ALTO.JK", "AMAG.JK",
    "AMAN.JK", "AMAR.JK", "AMFG.JK", "AMIN.JK", "AMMN.JK", "AMMS.JK", "AMOR.JK", "AMRT.JK",
    "ANDI.JK", "ANJT.JK", "ANTM.JK", "APEX.JK", "APIC.JK", "APII.JK", "APLI.JK", "APLN.JK",
    "ARCI.JK", "AREA.JK", "ARGO.JK", "ARII.JK", "ARKA.JK", "ARKO.JK", "ARMY.JK", "ARNA.JK",
    "ARTA.JK", "ARTI.JK", "ARTO.JK", "ASBI.JK", "ASDM.JK", "ASGR.JK", "ASHA.JK", "ASII.JK",
    "ASJT.JK", "ASLC.JK", "ASLI.JK", "ASMI.JK", "ASPI.JK", "ASRI.JK", "ASRM.JK", "ASSA.JK",
    "ATAP.JK", "ATIC.JK", "ATLA.JK", "AUTO.JK", "AVIA.JK", "AWAN.JK", "AXIO.JK", "AYAM.JK",
    "AYLS.JK", "BABP.JK", "BABY.JK", "BACA.JK", "BAIK.JK", "BAJA.JK", "BALI.JK", "BANK.JK",
    "BAPA.JK", "BAPI.JK", "BATA.JK", "BATR.JK", "BAUT.JK", "BAYU.JK", "BBCA.JK", "BBHI.JK",
    "BBKP.JK", "BBLD.JK", "BBMD.JK", "BBNI.JK", "BBRI.JK", "BBRM.JK", "BBSI.JK", "BBSS.JK",
    "BBTN.JK", "BBYB.JK", "BCAP.JK", "BCIC.JK", "BCIP.JK", "BDKR.JK", "BDMN.JK", "BEBS.JK",
    "BEEF.JK", "BEER.JK", "BEKS.JK", "BELI.JK", "BELL.JK", "BESS.JK", "BEST.JK", "BFIN.JK",
    "BGTG.JK", "BHAT.JK", "BHIT.JK", "BIKA.JK", "BIKE.JK", "BIMA.JK", "BINA.JK", "BINO.JK",
    "BIPI.JK", "BIPP.JK", "BIRD.JK", "BISI.JK", "BJBR.JK", "BJTM.JK", "BKDP.JK", "BKSL.JK",
    "BKSW.JK", "BLES.JK", "BLTA.JK", "BLTZ.JK", "BLUE.JK", "BMAS.JK", "BMBL.JK", "BMHS.JK",
    "BMRI.JK", "BMSR.JK", "BMTR.JK", "BNBA.JK", "BNBR.JK", "BNGA.JK", "BNII.JK", "BNLI.JK",
    "BOAT.JK", "BOBA.JK", "BOGA.JK", "BOLA.JK", "BOLT.JK", "BOSS.JK", "BPFI.JK", "BPII.JK",
    "BPTR.JK", "BRAM.JK", "BREN.JK", "BRIS.JK", "BRMS.JK", "BRNA.JK", "BRPT.JK", "BSBK.JK",
    "BSDE.JK", "BSIM.JK", "BSML.JK", "BSSR.JK", "BSWD.JK", "BTEK.JK", "BTEL.JK", "BTON.JK",
    "BTPN.JK", "BTPS.JK", "BUAH.JK", "BUDI.JK", "BUKA.JK", "BUKK.JK", "BULL.JK", "BUMI.JK",
    "BUVA.JK", "BVIC.JK", "BWPT.JK", "BYAN.JK", "CAKK.JK", "CAMP.JK", "CANI.JK", "CARE.JK",
    "CARS.JK", "CASA.JK", "CASH.JK", "CASS.JK", "CBMF.JK", "CBPE.JK", "CBRE.JK", "CBUT.JK",
    "CCSI.JK", "CEKA.JK", "CENT.JK", "CFIN.JK", "CGAS.JK", "CHEM.JK", "CHIP.JK", "CINT.JK",
    "CITA.JK", "CITY.JK", "CLAY.JK", "CLEO.JK", "CLPI.JK", "CMNP.JK", "CMNT.JK", "CMPP.JK",
    "CMRY.JK", "CNKO.JK", "CNMA.JK", "CNTX.JK", "COAL.JK", "COCO.JK", "COWL.JK", "CPIN.JK",
    "CPRI.JK", "CPRO.JK", "CRAB.JK", "CRSN.JK", "CSAP.JK", "CSIS.JK", "CSMI.JK", "CSRA.JK",
    "CTBN.JK", "CTRA.JK", "CTTH.JK", "CUAN.JK", "CYBR.JK", "DAAZ.JK", "DADA.JK", "DART.JK",
    "DATA.JK", "DAYA.JK", "DCII.JK", "DEAL.JK", "DEFI.JK", "DEPO.JK", "DEWA.JK", "DEWI.JK",
    "DFAM.JK", "DGIK.JK", "DGNS.JK", "DIGI.JK", "DILD.JK", "DIVA.JK", "DKFT.JK", "DLTA.JK",
    "DMAS.JK", "DMMX.JK", "DMND.JK", "DNAR.JK", "DNET.JK", "DOID.JK", "DOOH.JK", "DOSS.JK",
    "DPNS.JK", "DPUM.JK", "DRMA.JK", "DSFI.JK", "DSNG.JK", "DSSA.JK", "DUCK.JK", "DUTI.JK",
    "DVLA.JK", "DWGL.JK", "DYAN.JK", "EAST.JK", "ECII.JK", "EDGE.JK", "EKAD.JK", "ELIT.JK",
    "ELPI.JK", "ELSA.JK", "ELTY.JK", "EMDE.JK", "EMTK.JK", "ENAK.JK", "ENRG.JK", "ENVY.JK",
    "ENZO.JK", "EPAC.JK", "EPMT.JK", "ERAA.JK", "ERAL.JK", "ERTX.JK", "ESIP.JK", "ESSA.JK",
    "ESTA.JK", "ESTI.JK", "ETWA.JK", "EURO.JK", "EXCL.JK", "FAPA.JK", "FAST.JK", "FASW.JK",
    "FILM.JK", "FIMP.JK", "FIRE.JK", "FISH.JK", "FITT.JK", "FLMC.JK", "FMII.JK", "FOLK.JK",
    "FOOD.JK", "FORU.JK", "FORZ.JK", "FPNI.JK", "FREN.JK", "FUJI.JK", "FUTR.JK", "FWCT.JK",
    "GAMA.JK", "GDST.JK", "GDYR.JK", "GEMA.JK", "GEMS.JK", "GGRM.JK", "GGRP.JK", "GHON.JK",
    "GIAA.JK", "GJTL.JK", "GLOB.JK", "GLVA.JK", "GMFI.JK", "GMTD.JK", "GOLD.JK", "GOLF.JK",
    "GOLL.JK", "GOOD.JK", "GOTO.JK", "GPRA.JK", "GPSO.JK", "GRIA.JK", "GRPH.JK", "GRPM.JK",
    "GSMF.JK", "GTBO.JK", "GTRA.JK", "GTSI.JK", "GULA.JK", "GUNA.JK", "GWSA.JK", "GZCO.JK",
    "HADE.JK", "HAIS.JK", "HAJJ.JK", "HALO.JK", "HATM.JK", "HBAT.JK", "HDFA.JK", "HDIT.JK",
    "HDTX.JK", "HEAL.JK", "HELI.JK", "HERO.JK", "HEXA.JK", "HILL.JK", "HITS.JK", "HKMU.JK",
    "HMSP.JK", "HOKI.JK", "HOME.JK", "HOMI.JK", "HOPE.JK", "HOTL.JK", "HRME.JK", "HRTA.JK",
    "HRUM.JK", "HUMI.JK", "HYGN.JK", "IATA.JK", "IBFN.JK", "IBOS.JK", "IBST.JK", "ICBP.JK",
    "ICON.JK", "IDEA.JK", "IDPR.JK", "IFII.JK", "IFSH.JK", "IGAR.JK", "IIKP.JK", "IKAI.JK",
    "IKAN.JK", "IKBI.JK", "IKPM.JK", "IMAS.JK", "IMJS.JK", "IMPC.JK", "INAF.JK", "INAI.JK",
    "INCF.JK", "INCI.JK", "INCO.JK", "INDF.JK", "INDO.JK", "INDR.JK", "INDS.JK", "INDX.JK",
    "INDY.JK", "INET.JK", "INKP.JK", "INOV.JK", "INPC.JK", "INPP.JK", "INPS.JK", "INRU.JK",
    "INTA.JK", "INTD.JK", "INTP.JK", "IOTF.JK", "IPAC.JK", "IPCC.JK", "IPCM.JK", "IPOL.JK",
    "IPPE.JK", "IPTV.JK", "IRRA.JK", "IRSX.JK", "ISAP.JK", "ISAT.JK", "ISEA.JK", "ISSP.JK",
    "ITIC.JK", "ITMA.JK", "ITMG.JK", "JARR.JK", "JAST.JK", "JATI.JK", "JAWA.JK", "JAYA.JK",
    "JECC.JK", "JGLE.JK", "JIHD.JK", "JKON.JK", "JKSW.JK", "JMAS.JK", "JPFA.JK", "JRPT.JK",
    "JSKY.JK", "JSMR.JK", "JSPT.JK", "JTPE.JK", "KAEF.JK", "KARW.JK", "KAYU.JK", "KBAG.JK",
    "KBLI.JK", "KBLM.JK", "KBLV.JK", "KBRI.JK", "KDSI.JK", "KDTN.JK", "KEEN.JK", "KEJU.JK",
    "KETR.JK", "KIAS.JK", "KICI.JK", "KIJA.JK", "KING.JK", "KINO.JK", "KIOS.JK", "KJEN.JK",
    "KKES.JK", "KKGI.JK", "KLAS.JK", "KLBF.JK", "KLIN.JK", "KMDS.JK", "KMTR.JK", "KOBX.JK",
    "KOCI.JK", "KOIN.JK", "KOKA.JK", "KONI.JK", "KOPI.JK", "KOTA.JK", "KPAL.JK", "KPAS.JK",
    "KPIG.JK", "KRAH.JK", "KRAS.JK", "KREN.JK", "KRYA.JK", "KUAS.JK", "LABA.JK", "LABS.JK",
    "LAJU.JK", "LAND.JK", "LAPD.JK", "LCGP.JK", "LCKM.JK", "LEAD.JK", "LFLO.JK", "LIFE.JK",
    "LINK.JK", "LION.JK", "LIVE.JK", "LMAS.JK", "LMAX.JK", "LMPI.JK", "LMSH.JK", "LOPI.JK",
    "LPCK.JK", "LPGI.JK", "LPIN.JK", "LPKR.JK", "LPLI.JK", "LPPF.JK", "LPPS.JK", "LRNA.JK",
    "LSIP.JK", "LTLS.JK", "LUCK.JK", "LUCY.JK", "MABA.JK", "MAGP.JK", "MAHA.JK", "MAIN.JK",
    "MAMI.JK", "MANG.JK", "MAPA.JK", "MAPB.JK", "MAPI.JK", "MARI.JK", "MARK.JK", "MASA.JK",
    "MASB.JK", "MAXI.JK", "MAYA.JK", "MBAP.JK", "MBMA.JK", "MBSS.JK", "MBTO.JK", "MCAS.JK",
    "MCOL.JK", "MCOR.JK", "MDIA.JK", "MDKA.JK", "MDKI.JK", "MDLN.JK", "MDRN.JK", "MEDC.JK",
    "MEDS.JK", "MEGA.JK", "MEJA.JK", "MENN.JK", "MERK.JK", "META.JK", "MFIN.JK", "MFMI.JK",
    "MGLV.JK", "MGNA.JK", "MGRO.JK", "MHKI.JK", "MICE.JK", "MIDI.JK", "MIKA.JK", "MINA.JK",
    "MIRA.JK", "MITI.JK", "MKAP.JK", "MKNT.JK", "MKPI.JK", "MKTR.JK", "MLBI.JK", "MLIA.JK",
    "MLPL.JK", "MLPT.JK", "MMIX.JK", "MMLP.JK", "MNCN.JK", "MOLI.JK", "MORA.JK", "MPIX.JK",
    "MPMX.JK", "MPOW.JK", "MPPA.JK", "MPRO.JK", "MPXL.JK", "MRAT.JK", "MREI.JK", "MSIE.JK",
    "MSIN.JK", "MSJA.JK", "MSKY.JK", "MSTI.JK", "MTDL.JK", "MTEL.JK", "MTFN.JK", "MTLA.JK",
    "MTMH.JK", "MTPS.JK", "MTRA.JK", "MTSM.JK", "MTWI.JK", "MUTU.JK", "MYOH.JK", "MYOR.JK",
    "MYRX.JK", "MYTX.JK", "NAIK.JK", "NANO.JK", "NASA.JK", "NASI.JK", "NATO.JK", "NAYZ.JK",
    "NCKL.JK", "NELY.JK", "NEST.JK", "NETV.JK", "NFCX.JK", "NICE.JK", "NICK.JK", "NICL.JK",
    "NIKL.JK", "NINE.JK", "NIPS.JK", "NIRO.JK", "NISP.JK", "NOBU.JK", "NPGF.JK", "NRCA.JK",
    "NSSS.JK", "NTBK.JK", "NUSA.JK", "NZIA.JK", "OASA.JK", "OBMD.JK", "OCAP.JK", "OILS.JK",
    "OKAS.JK", "OLIV.JK", "OMED.JK", "OMRE.JK", "OPMS.JK", "PACK.JK", "PADA.JK", "PADI.JK",
    "PALM.JK", "PAMG.JK", "PANI.JK", "PANR.JK", "PANS.JK", "PART.JK", "PBID.JK", "PBRX.JK",
    "PBSA.JK", "PCAR.JK", "PDES.JK", "PDPP.JK", "PEGE.JK", "PEHA.JK", "PEVE.JK", "PGAS.JK",
    "PGEO.JK", "PGJO.JK", "PGLI.JK", "PGUN.JK", "PICO.JK", "PIPA.JK", "PJAA.JK", "PKPK.JK",
    "PLAN.JK", "PLAS.JK", "PLIN.JK", "PMJS.JK", "PMMP.JK", "PNBN.JK", "PNBS.JK", "PNGO.JK",
    "PNIN.JK", "PNLF.JK", "PNSE.JK", "POLA.JK", "POLI.JK", "POLL.JK", "POLU.JK", "POLY.JK",
    "POOL.JK", "PORT.JK", "POSA.JK", "POWR.JK", "PPGL.JK", "PPRE.JK", "PPRI.JK", "PPRO.JK",
    "PRAS.JK", "PRAY.JK", "PRDA.JK", "PRIM.JK", "PSAB.JK", "PSDN.JK", "PSGO.JK", "PSKT.JK",
    "PSSI.JK", "PTBA.JK", "PTDU.JK", "PTIS.JK", "PTMP.JK", "PTMR.JK", "PTPP.JK", "PTPS.JK",
    "PTPW.JK", "PTRO.JK", "PTSN.JK", "PTSP.JK", "PUDP.JK", "PURA.JK", "PURE.JK", "PURI.JK",
    "PWON.JK", "PYFA.JK", "PZZA.JK", "RAAM.JK", "RAFI.JK", "RAJA.JK", "RALS.JK", "RANC.JK",
    "RBMS.JK", "RCCC.JK", "RDTX.JK", "REAL.JK", "RELF.JK", "RELI.JK", "RGAS.JK", "RICY.JK",
    "RIGS.JK", "RIMO.JK", "RISE.JK", "RMKE.JK", "RMKO.JK", "ROCK.JK", "RODA.JK", "RONY.JK",
    "ROTI.JK", "RSCH.JK", "RSGK.JK", "RUIS.JK", "RUNS.JK", "SAFE.JK", "SAGE.JK", "SAME.JK",
    "SAMF.JK", "SAPX.JK", "SATU.JK", "SBAT.JK", "SBMA.JK", "SCCO.JK", "SCMA.JK", "SCNP.JK",
    "SCPI.JK", "SDMU.JK", "SDPC.JK", "SDRA.JK", "SEMA.JK", "SFAN.JK", "SGER.JK", "SGRO.JK",
    "SHID.JK", "SHIP.JK", "SICO.JK", "SIDO.JK", "SILO.JK", "SIMA.JK", "SIMP.JK", "SINI.JK",
    "SIPD.JK", "SKBM.JK", "SKLT.JK", "SKRN.JK", "SKYB.JK", "SLIS.JK", "SMAR.JK", "SMBR.JK",
    "SMCB.JK", "SMDM.JK", "SMDR.JK", "SMGA.JK", "SMGR.JK", "SMIL.JK", "SMKL.JK", "SMKM.JK",
    "SMLE.JK", "SMMA.JK", "SMMT.JK", "SMRA.JK", "SMRU.JK", "SMSM.JK", "SNLK.JK", "SOCI.JK",
    "SOFA.JK", "SOHO.JK", "SOLA.JK", "SONA.JK", "SOSS.JK", "SOTS.JK", "SOUL.JK", "SPMA.JK",
    "SPRE.JK", "SPTO.JK", "SQMI.JK", "SRAJ.JK", "SRIL.JK", "SRSN.JK", "SRTG.JK", "SSIA.JK",
    "SSMS.JK", "SSTM.JK", "STAA.JK", "STAR.JK", "STRK.JK", "STTP.JK", "SUGI.JK", "SULI.JK",
    "SUNI.JK", "SUPR.JK", "SURE.JK", "SURI.JK", "SWAT.JK", "SWID.JK", "TALF.JK", "TAMA.JK",
    "TAMU.JK", "TAPG.JK", "TARA.JK", "TAXI.JK", "TAYS.JK", "TBIG.JK", "TBLA.JK", "TBMS.JK",
    "TCID.JK", "TCPI.JK", "TDPM.JK", "TEBE.JK", "TECH.JK", "TELE.JK", "TFAS.JK", "TFCO.JK",
    "TGKA.JK", "TGRA.JK", "TGUK.JK", "TIFA.JK", "TINS.JK", "TIRA.JK", "TIRT.JK", "TKIM.JK",
    "TLDN.JK", "TLKM.JK", "TMAS.JK", "TMPO.JK", "TNCA.JK", "TOBA.JK", "TOOL.JK", "TOPS.JK",
    "TOSK.JK", "TOTL.JK", "TOTO.JK", "TOWR.JK", "TOYS.JK", "TPIA.JK", "TPMA.JK", "TRAM.JK",
    "TRGU.JK", "TRIL.JK", "TRIM.JK", "TRIN.JK", "TRIO.JK", "TRIS.JK", "TRJA.JK", "TRON.JK",
    "TRST.JK", "TRUE.JK", "TRUK.JK", "TRUS.JK", "TSPC.JK", "TUGU.JK", "TYRE.JK", "UANG.JK",
    "UCID.JK", "UDNG.JK", "UFOE.JK", "ULTJ.JK", "UNIC.JK", "UNIQ.JK", "UNIT.JK", "UNSP.JK",
    "UNTD.JK", "UNTR.JK", "UNVR.JK", "URBN.JK", "UVCR.JK", "VAST.JK", "VERN.JK", "VICI.JK",
    "VICO.JK", "VINS.JK", "VISI.JK", "VIVA.JK", "VKTR.JK", "VOKS.JK", "VRNA.JK", "VTNY.JK",
    "WAPO.JK", "WEGE.JK", "WEHA.JK", "WGSH.JK", "WICO.JK", "WIDI.JK", "WIFI.JK", "WIIM.JK",
    "WIKA.JK", "WINE.JK", "WINR.JK", "WINS.JK", "WIRG.JK", "WMPP.JK", "WMUU.JK", "WOMF.JK",
    "WOOD.JK", "WOWS.JK", "WSBP.JK", "WSKT.JK", "WTON.JK", "YELO.JK", "YPAS.JK", "YULE.JK",
    "ZATA.JK", "ZBRA.JK", "ZINC.JK", "ZONE.JK", "ZYRX.JK",
]

# --- US ------------------------------------------------------------------------------
# Yahoo Finance dual-class convention: dot replaced with dash (BRK.B -> BRK-B).

# Curated quick-scan list of the most active large-caps (faster than the full S&P 500).
US_LARGE_CAP: list[str] = [
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA",
    "BRK-B", "JPM", "V", "MA", "UNH", "XOM", "JNJ", "PG", "HD", "CVX",
    "LLY", "ABBV", "PEP", "KO", "AVGO", "MRK", "COST", "WMT", "ORCL",
    "CRM", "ADBE", "MCD", "ACN", "BAC", "WFC", "TMO", "ABT", "DIS",
    "CSCO", "PFE", "NFLX", "INTC", "AMD", "QCOM", "TXN", "IBM", "NKE",
    "GE", "BA", "CAT", "GS", "MS", "AXP", "BLK", "C", "PM", "RTX",
    "HON", "LIN", "AMAT", "BKNG", "PYPL", "INTU", "AMGN", "DE", "GILD",
    "ISRG", "VRTX", "REGN", "ADP", "MDT", "SCHW", "T", "VZ", "CMCSA",
    "TMUS", "F", "GM", "UPS", "FDX", "LMT", "NOC", "MO", "SBUX",
    "TGT", "LOW", "CVS", "ELV", "BMY", "DHR", "ANET", "NOW", "PANW",
    "SHOP", "UBER", "ABNB", "PLTR", "COIN", "SNOW", "MU", "MELI", "MARA",
    "DDOG", "CRWD", "NET", "ZS", "SQ", "SOFI",
]

# Dow Jones Industrial Average — 30 mega-caps (also subset of S&P 500).
DOW30: list[str] = [
    "AAPL", "AMGN", "AMZN", "AXP", "BA", "CAT", "CRM", "CSCO",
    "CVX", "DIS", "GS", "HD", "HON", "IBM", "JNJ", "JPM",
    "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "NVDA", "PG",
    "SHW", "TRV", "UNH", "V", "VZ", "WMT",
]

# NASDAQ-100 — full index (101 tickers due to dual-class shares).
NASDAQ100: list[str] = sorted(set([
    "AAPL", "ABNB", "ADBE", "ADI", "ADP", "ADSK", "AEP", "ALNY",
    "AMAT", "AMD", "AMGN", "AMZN", "APP", "ARM", "ASML", "AVGO",
    "AXON", "BKNG", "BKR", "CCEP", "CDNS", "CEG", "CHTR", "CMCSA",
    "COST", "CPRT", "CRWD", "CSCO", "CSGP", "CSX", "CTAS", "CTSH",
    "DASH", "DDOG", "DXCM", "EA", "EXC", "FANG", "FAST", "FER",
    "FTNT", "GEHC", "GILD", "GOOG", "GOOGL", "HON", "IDXX", "INSM",
    "INTC", "INTU", "ISRG", "KDP", "KHC", "KLAC", "LIN", "LRCX",
    "MAR", "MCHP", "MDLZ", "MELI", "META", "MNST", "MPWR", "MRVL",
    "MSFT", "MSTR", "MU", "NFLX", "NVDA", "NXPI", "ODFL", "ORLY",
    "PANW", "PAYX", "PCAR", "PDD", "PEP", "PLTR", "PYPL", "QCOM",
    "REGN", "ROP", "ROST", "SBUX", "SHOP", "SNDK", "SNPS", "STX",
    "TMUS", "TRI", "TSLA", "TTWO", "TXN", "VRSK", "VRTX", "WBD",
    "WDAY", "WDC", "WMT", "XEL", "ZS",
]))

# S&P 500 — full index (503 tickers due to dual-class shares).
SP500: list[str] = sorted(set([
    "A", "AAPL", "ABBV", "ABNB", "ABT", "ACGL", "ACN", "ADBE",
    "ADI", "ADM", "ADP", "ADSK", "AEE", "AEP", "AES", "AFL",
    "AIG", "AIZ", "AJG", "AKAM", "ALB", "ALGN", "ALL", "ALLE",
    "AMAT", "AMCR", "AMD", "AME", "AMGN", "AMP", "AMT", "AMZN",
    "ANET", "AON", "AOS", "APA", "APD", "APH", "APO", "APP",
    "APTV", "ARE", "ARES", "ATO", "AVB", "AVGO", "AVY", "AWK",
    "AXON", "AXP", "AZO", "BA", "BAC", "BALL", "BAX", "BBY",
    "BDX", "BEN", "BF-B", "BG", "BIIB", "BK", "BKNG", "BKR",
    "BLDR", "BLK", "BMY", "BR", "BRK-B", "BRO", "BSX", "BX",
    "BXP", "C", "CAG", "CAH", "CARR", "CASY", "CAT", "CB",
    "CBOE", "CBRE", "CCI", "CCL", "CDNS", "CDW", "CEG", "CF",
    "CFG", "CHD", "CHRW", "CHTR", "CI", "CIEN", "CINF", "CL",
    "CLX", "CMCSA", "CME", "CMG", "CMI", "CMS", "CNC", "CNP",
    "COF", "COHR", "COIN", "COO", "COP", "COR", "COST", "CPAY",
    "CPB", "CPRT", "CPT", "CRH", "CRL", "CRM", "CRWD", "CSCO",
    "CSGP", "CSX", "CTAS", "CTRA", "CTSH", "CTVA", "CVNA", "CVS",
    "CVX", "D", "DAL", "DASH", "DD", "DDOG", "DE", "DECK",
    "DELL", "DG", "DGX", "DHI", "DHR", "DIS", "DLR", "DLTR",
    "DOC", "DOV", "DOW", "DPZ", "DRI", "DTE", "DUK", "DVA",
    "DVN", "DXCM", "EA", "EBAY", "ECL", "ED", "EFX", "EG",
    "EIX", "EL", "ELV", "EME", "EMR", "EOG", "EPAM", "EQIX",
    "EQR", "EQT", "ERIE", "ES", "ESS", "ETN", "ETR", "EVRG",
    "EW", "EXC", "EXE", "EXPD", "EXPE", "EXR", "F", "FANG",
    "FAST", "FCX", "FDS", "FDX", "FE", "FFIV", "FICO", "FIS",
    "FISV", "FITB", "FIX", "FOX", "FOXA", "FRT", "FSLR", "FTNT",
    "FTV", "GD", "GDDY", "GE", "GEHC", "GEN", "GEV", "GILD",
    "GIS", "GL", "GLW", "GM", "GNRC", "GOOG", "GOOGL", "GPC",
    "GPN", "GRMN", "GS", "GWW", "HAL", "HAS", "HBAN", "HCA",
    "HD", "HIG", "HII", "HLT", "HON", "HOOD", "HPE", "HPQ",
    "HRL", "HSIC", "HST", "HSY", "HUBB", "HUM", "HWM", "IBKR",
    "IBM", "ICE", "IDXX", "IEX", "IFF", "INCY", "INTC", "INTU",
    "INVH", "IP", "IQV", "IR", "IRM", "ISRG", "IT", "ITW",
    "IVZ", "J", "JBHT", "JBL", "JCI", "JKHY", "JNJ", "JPM",
    "KDP", "KEY", "KEYS", "KHC", "KIM", "KKR", "KLAC", "KMB",
    "KMI", "KO", "KR", "KVUE", "L", "LDOS", "LEN", "LH",
    "LHX", "LII", "LIN", "LITE", "LLY", "LMT", "LNT", "LOW",
    "LRCX", "LULU", "LUV", "LVS", "LYB", "LYV", "MA", "MAA",
    "MAR", "MAS", "MCD", "MCHP", "MCK", "MCO", "MDLZ", "MDT",
    "MET", "META", "MGM", "MKC", "MLM", "MMM", "MNST", "MO",
    "MOS", "MPC", "MPWR", "MRK", "MRNA", "MRSH", "MS", "MSCI",
    "MSFT", "MSI", "MTB", "MTD", "MU", "NCLH", "NDAQ", "NDSN",
    "NEE", "NEM", "NFLX", "NI", "NKE", "NOC", "NOW", "NRG",
    "NSC", "NTAP", "NTRS", "NUE", "NVDA", "NVR", "NWS", "NWSA",
    "NXPI", "O", "ODFL", "OKE", "OMC", "ON", "ORCL", "ORLY",
    "OTIS", "OXY", "PANW", "PAYX", "PCAR", "PCG", "PEG", "PEP",
    "PFE", "PFG", "PG", "PGR", "PH", "PHM", "PKG", "PLD",
    "PLTR", "PM", "PNC", "PNR", "PNW", "PODD", "POOL", "PPG",
    "PPL", "PRU", "PSA", "PSKY", "PSX", "PTC", "PWR", "PYPL",
    "Q", "QCOM", "RCL", "REG", "REGN", "RF", "RJF", "RL",
    "RMD", "ROK", "ROL", "ROP", "ROST", "RSG", "RTX", "RVTY",
    "SATS", "SBAC", "SBUX", "SCHW", "SHW", "SJM", "SLB", "SMCI",
    "SNA", "SNDK", "SNPS", "SO", "SOLV", "SPG", "SPGI", "SRE",
    "STE", "STLD", "STT", "STX", "STZ", "SW", "SWK", "SWKS",
    "SYF", "SYK", "SYY", "T", "TAP", "TDG", "TDY", "TECH",
    "TEL", "TER", "TFC", "TGT", "TJX", "TKO", "TMO", "TMUS",
    "TPL", "TPR", "TRGP", "TRMB", "TROW", "TRV", "TSCO", "TSLA",
    "TSN", "TT", "TTD", "TTWO", "TXN", "TXT", "TYL", "UAL",
    "UBER", "UDR", "UHS", "ULTA", "UNH", "UNP", "UPS", "URI",
    "USB", "V", "VICI", "VLO", "VLTO", "VMC", "VRSK", "VRSN",
    "VRT", "VRTX", "VST", "VTR", "VTRS", "VZ", "WAB", "WAT",
    "WBD", "WDAY", "WDC", "WEC", "WELL", "WFC", "WM", "WMB",
    "WMT", "WRB", "WSM", "WST", "WTW", "WY", "WYNN", "XEL",
    "XOM", "XYL", "XYZ", "YUM", "ZBH", "ZBRA", "ZTS",
]))


def market_universes() -> dict[str, dict[str, list[str]]]:
    """Return {market: {label: tickers}} mapping."""
    return {
        "IDX": {
            # Core liquidity tiers (most likely starting point for screening).
            "IDX30": IDX30,
            "LQ45": LQ45,
            "IDX80": IDX80,
            "Kompas100": KOMPAS100,
            # Themed indices.
            "JII (Syariah 30)": JII,
            "JII70 (Syariah 70)": JII70,
            "IDXBUMN20": IDXBUMN20,
            "IDXHIDIV20 (High Dividend)": IDXHIDIV20,
            # Sectoral (IDX-IC classification — full sector membership).
            "Sector: Basic Materials": IDXBASIC,
            "Sector: Consumer Cyclicals": IDXCYCLIC,
            "Sector: Consumer Non-Cyclicals": IDXNONCYC,
            "Sector: Energy": IDXENERGY,
            "Sector: Financials": IDXFINANCE,
            "Sector: Healthcare": IDXHEALTH,
            "Sector: Industrials": IDXINDUST,
            "Sector: Infrastructure": IDXINFRA,
            "Sector: Properties & Real Estate": IDXPROPERT,
            "Sector: Technology": IDXTECHNO,
            "Sector: Transportation & Logistics": IDXTRANS,
            # Full IDX universe — heavy scan (~941 tickers, ~10-15 minutes).
            "IHSG (all listed, ~941)": IHSG,
        },
        "US": {
            "Dow 30": DOW30,
            "Large Cap (top ~100)": US_LARGE_CAP,
            "NASDAQ 100": NASDAQ100,
            "S&P 500": SP500,
        },
    }


def list_markets() -> list[str]:
    return list(market_universes().keys())


def list_universes(market: str) -> list[str]:
    return list(market_universes().get(market, {}).keys())


def get_universe(market: str, name: str) -> list[str]:
    return market_universes().get(market, {}).get(name, [])


def is_idx(symbol: str) -> bool:
    return symbol.upper().endswith(".JK")


def market_of(symbol: str) -> str:
    return "IDX" if is_idx(symbol) else "US"


def currency_of(symbol: str) -> str:
    return "IDR" if is_idx(symbol) else "USD"

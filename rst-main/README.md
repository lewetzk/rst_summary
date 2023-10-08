# rst

### Meeting 25.06.22 - 

#### Fragestellung:
Kann aus einer rhetorischen Struktur eines Textes mittels der Strong Nuclearity Hypothese eine passende Zusammenfassung (Kernaussage falls nur ein Satz) erstellt werden?

#### Bericht:
Definiere im Bericht Zusammenfassung/Kernaussage
4-5 Seiten
https://www.overleaf.com/6981169414jgmxtncnfhhq
#### Quellen:
- [Barzilay et al entity-based coherence für Auswertung](https://aclanthology.org/J08-1001.pdf) (Clusterbildung) 
- Framework https://github.com/karins/CoherenceFramework  ([Paper hier](https://aclanthology.org/L16-1649/))

#### TODO
- [x] Algorithmus entwickeln zum Durchlaufen der Baumstruktur entlang der Nuklei (rekursiv oder ifelse) - welche Fälle könnten passieren? (Multinukleare Rel)
- [x] Stede Meeting anfragen: Mo nachmittag (am besten um) 13 Uhr oder später, Di bis 16 Uhr
        - welche Daten könnten wir bekommen? Wieviele weitere (PCC-)Kommentare RST-annotiert + Kernaussagen davon?
        - wann könnten wir die bekommen?
        - wie genau stellt er sich das entity-based grid vor? - sollen wir das selber bauen oder  anwenden?
- [x] Funktioniert das CoherenceFramework? Ausprobieren
        - Nicht wirklich nuetzlich, Python-Code zu alt. Selber entity grid aufbauen, da in Daten ja subj/obj markiert sind 


### 1. Stede-Meeting Mo 27.06.22, 10 Uhr Zoom

Zusammenfassungen unserer RST-Implementation nach SNH:
--> Fokus bei Evaluierung auf Kohärenz der Zusammenfassungen
PCC-Korpus hat auch Syntaxparses mit grammatischen Rollen (subj/obj), aus denen ein entity grid gebaut werden kann

Vergleiche entity grids der RST-ZSF mit:
- baseline summary: wähle ersten, mittleren und letzten Satz als ZSF
- random baseline: wähle 2 random sätze als ZSF
- empirisch: 5 Pers bewerten gewissen Anzahl an ZSF auf kohärenz mittels Fragebogen

- Zusammenfassungen Bert-Modell: wie könnten wir die mit reinbringen? human bewertung?!
--> für Finetuning könnten wir noch mal 1000 unannotierte maz-kommentare von Stede bekommen


Zwischenmeeting in 2-3 Wochen zu ersten Zwischenschritten/Problemen etc

### Nächstes RST-Meeting in der Gruppe Do, 30.06.22 um 10 Uhr
#### TODO


- [x] Aus allen Gold maz-texte mit tree_traverse ZSF erstellen und mit Gold-Kernaussagen Stringvergleich abgleichen (dani)
- [x] Bert-Model [GermanTextSummarisationContestSwissText](https://www.swisstext.org/2019/shared-task/german-text-summarization-challenge.html) und [MLSum](https://github.com/ThomasScialom/MLSUM) Zsf (Seba)
- [x] baseline summary (philine) - random oder token-basiert
- [x] random summary (lea) - verchiedene random-ansätze


### Nächstes RST- Meeting Fr 08.07.22, 12 Uhr
- Entity-based paper nicht so ganz klar - wir brauchen neues Meeting mit Stede?? oder geht auch so?

- [x] Paper Entity-based coherence lesen (alle)
- Die große Fragestellung: Wie bauen wir das entity grid model?
- [x] grammatical roles und koferenzketten aus mmax-Dateien filtern 
        -> pro entität eine kette und pro kettenglied eine grammatical role
- [ ] Funktion zum entity grid erstellen aus grammaticalroles/kettenglied (angewendet auf Gold-ZSF, SNH-ZSF Baseline-ZSF, random-ZSF)
- [ ] Vektoren aus Wahrscheinlichkeiten der 16 transitions (zw S, O, X, -)
- [x] Gold-Kommentare in train/test data unterteilen (80/20): gold_train, gold_test directories
- [x] Summaries speichern in txt Dateien: filename ist maz-xxx, ein Satz pro Zeile (mit \n am Ende)
- [x] summaries in summary-art-ordner (baseline, random, snh, gold) speichern
- [x] Conll-Parser checken - Koref-Kette für z.B. maz-10010 ist in role-file schlechter als in conll-file

Bemerkungen:
- Schlecht annotierte Gold-Kommentare werden in buggy_goldies-Ordner verschoben ("Die schlechten ins Kröpfchen...")


### Nächstes RST- Meeting Fr 15.07.22, 12 Uhr

#### Besprechen
- Entity Grid besprechen und inspizieren
- wie erstellen wir die Vektoren aus den transitions?
- was bleibt sonst noch zu tun?

#### TODO
- [x] Funktion zum entity grid erstellen aus grammaticalroles/kettenglied (angewendet auf Gold-ZSF, SNH-ZSF Baseline-ZSF, random-ZSF)
- [x] Zsf SNH, baseline, random nur für Zsf in gold_test set! alle anderen rausschmeißen
- [x] bei SNH, baseline, random Satznummern abspeichern in folgender Form:
        "maz-10110": {
        "summary": [
        "Zukunftsinvestitionen",
        "Das sollte honoriert werden"
        ],
        "sent_num": [],
        "ent_grid": #entgrids für die sent_nums
        } (Ph, Lea, Dani)
- [x] Vektoren aus Wahrscheinlichkeiten der 16 transitions (zw S, O, X, -) 
        1 Zsf = 1 dokument - (Wahrscheinlichkeiten der Trans. addieren sich auf 1 pro Zsf)
- [ ] SVM trainieren mit gold_train set: Gewicht w für Transitionsvektoren

#### Bericht: 
1. Zsf nicht alle gleiche Satzanzahl - könnte verzerren
2. Dok/Zsf sind sehr klein - hat das evtl Einfluss?
3. Problem mit Qualität der Annotationen wirkt sich auf entity grid aus



### Nächstes RST- Meeting Mi 27.07.22, 10 Uhr
Erste Ergebnisse (script human_readable_rank_results.py ausführen):

snh besser als gold: 39 vs. gold besser als snh: 134
snh besser als baseline: 83 vs. baseline besser als snh: 90
snh besser als neural25: 84 vs. neural25 besser als snh: 89
snh besser als neural50: 79 vs. neural50 besser als snh: 94
snh besser als random: 113 vs. random besser als snh: 60

Gesamtzahl Kommentare: 173

No of random_first: 0
No of random_second: 6

No of gold_first: 82
No of gold_second: 45

No of baseline_first: 7
No of baseline_second: 34

No of neural25_first: 28
No of neural25_second: 28

No of neural50_first: 28
No of neural50_second: 29

No of snh_first: 28
No of snh_second: 31

Beste Zusammenfassungen: gold_first



### TODO
- Plot anpassen: x-/y-achse beschriften, dickere lines
- Plot in Präsi einfügen

"""
BALE V11 Clause Rewrite Engine
Suggests safer alternative clause language using contrastive embedding search.

Innovation: No legal AI tool generates clause rewrites without an LLM.
BALE does it using the same embedding model already loaded, by searching
a curated library of "gold standard" clause templates.
"""
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import logging
import difflib

logger = logging.getLogger("bale_v11_rewrite")


# ==================== CLAUSE TEMPLATE BANK ====================
# Each clause type has safe/balanced templates at different risk levels.
# These are drawn from best-practice commercial contract language.

CLAUSE_TEMPLATES: Dict[str, List[Dict[str, str]]] = {
    "indemnification": [
        {
            "level": "balanced",
            "text": "Each party shall indemnify, defend, and hold harmless the other party from and against any third-party claims, losses, damages, and reasonable expenses (including attorneys' fees) arising from (a) the indemnifying party's material breach of this Agreement, (b) the indemnifying party's negligence or willful misconduct, or (c) the indemnifying party's violation of applicable law. The indemnified party shall provide prompt written notice and reasonable cooperation.",
            "risk_score": 25,
            "jurisdiction": "general",
        },
        {
            "level": "protective",
            "text": "Each party shall indemnify the other party against third-party claims arising directly from the indemnifying party's breach of its representations and warranties under this Agreement. Indemnification obligations are subject to the limitations of liability set forth herein. The indemnified party shall mitigate damages where commercially reasonable.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "standard",
            "text": "Provider shall indemnify Client against third-party intellectual property infringement claims arising from Client's authorized use of the Services. Client shall indemnify Provider against claims arising from Client's data or Client's use of the Services in violation of this Agreement. Each party's indemnification obligations are conditioned upon prompt notice and sole control of the defense.",
            "risk_score": 30,
            "jurisdiction": "general",
        },
        {
            "level": "mutual",
            "text": "Each party agrees to indemnify and hold harmless the other party from losses arising out of the indemnifying party's material breach of this Agreement or its negligent acts. The maximum aggregate indemnification liability of either party shall not exceed the total fees paid or payable under this Agreement during the twelve-month period preceding the claim.",
            "risk_score": 22,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "Chaque partie s'engage a indemniser et garantir l'autre partie contre toute reclamation de tiers decoulant d'une violation substantielle du present contrat, de la negligence ou de la faute intentionnelle de la partie responsable. L'indemnisation est soumise aux limitations de responsabilite prevues aux presentes.",
            "risk_score": 25,
            "jurisdiction": "FR",
        },
    ],
    "limitation_of_liability": [
        {
            "level": "balanced",
            "text": "Neither party's aggregate liability under this Agreement shall exceed the total amounts paid or payable by Client during the twelve (12) months preceding the event giving rise to liability. Neither party shall be liable for indirect, incidental, consequential, special, or punitive damages, regardless of the theory of liability. These limitations shall not apply to breaches of confidentiality, indemnification obligations, or willful misconduct.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "protective",
            "text": "In no event shall either party's total aggregate liability exceed the greater of (a) the fees paid under this Agreement in the preceding twelve months, or (b) one hundred thousand dollars ($100,000). This limitation applies to all causes of action in the aggregate. Exclusions: fraud, gross negligence, willful misconduct, death or personal injury, and intellectual property indemnification.",
            "risk_score": 18,
            "jurisdiction": "general",
        },
        {
            "level": "standard",
            "text": "Except for each party's indemnification obligations, neither party shall be liable for any indirect, incidental, special, consequential, or exemplary damages. Each party's maximum aggregate liability shall be limited to the amounts paid under this Agreement during the twelve months prior to the claim.",
            "risk_score": 25,
            "jurisdiction": "general",
        },
        {
            "level": "tiered",
            "text": "Liability is tiered as follows: (a) General liability cap: twelve months of fees; (b) Data breach liability cap: twenty-four months of fees; (c) IP infringement and willful misconduct: uncapped. Neither party shall be liable for loss of profits, revenue, data, or business opportunities except where arising from willful misconduct.",
            "risk_score": 22,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "La responsabilite totale de chaque partie au titre du present contrat est limitee au montant des sommes versees au cours des douze mois precedant le fait generateur. Sont exclues les pertes indirectes, sauf en cas de faute lourde ou intentionnelle.",
            "risk_score": 22,
            "jurisdiction": "FR",
        },
    ],
    "termination": [
        {
            "level": "balanced",
            "text": "Either party may terminate this Agreement: (a) for convenience upon sixty (60) days' written notice; (b) for material breach if the breaching party fails to cure within thirty (30) days of written notice specifying the breach; or (c) immediately upon the other party's insolvency, bankruptcy filing, or assignment for benefit of creditors. Upon termination, all accrued obligations survive, and each party shall return or destroy the other's confidential information.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "protective",
            "text": "Either party may terminate for material breach with thirty (30) days' written notice and cure period. Termination for convenience requires ninety (90) days' notice. The following survive termination: confidentiality (3 years), limitation of liability, indemnification, and any accrued payment obligations. Provider shall assist with transition for up to ninety days.",
            "risk_score": 18,
            "jurisdiction": "general",
        },
        {
            "level": "standard",
            "text": "This Agreement may be terminated by either party for cause upon thirty days' written notice if the other party materially breaches and fails to cure. Either party may terminate for convenience upon sixty days' prior written notice. All fees through the termination date remain payable.",
            "risk_score": 25,
            "jurisdiction": "general",
        },
        {
            "level": "with_transition",
            "text": "Upon termination or expiration, Provider shall (a) continue providing Services during a transition period of up to ninety (90) days at standard rates, (b) provide all Client data in a standard machine-readable format, and (c) certify destruction of Client confidential information within thirty days.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "Chaque partie peut resilier le contrat en cas de manquement grave non remedie dans les trente jours suivant mise en demeure. La resiliation pour convenance est possible moyennant un preavis de soixante jours. Les obligations accumulees et les clauses de confidentialite survivent a la resiliation.",
            "risk_score": 22,
            "jurisdiction": "FR",
        },
    ],
    "confidentiality": [
        {
            "level": "balanced",
            "text": "Each party agrees to maintain the confidentiality of the other party's Confidential Information using at least the same degree of care it uses to protect its own confidential information, but no less than reasonable care. Confidential Information excludes information that: (a) is publicly available, (b) was known prior to disclosure, (c) is independently developed, or (d) is disclosed pursuant to legal requirement with prior notice. Obligations continue for three (3) years after termination.",
            "risk_score": 15,
            "jurisdiction": "general",
        },
        {
            "level": "standard",
            "text": "Neither party shall disclose the other's Confidential Information to any third party without prior written consent, except to employees and contractors with a need to know who are bound by confidentiality obligations at least as protective as those herein. The receiving party shall promptly notify the disclosing party of any unauthorized disclosure.",
            "risk_score": 18,
            "jurisdiction": "general",
        },
        {
            "level": "protective",
            "text": "All Confidential Information remains the property of the disclosing party. The receiving party shall use Confidential Information solely for performing its obligations under this Agreement. Upon termination or request, the receiving party shall return or destroy all Confidential Information and certify such destruction in writing.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "mutual_with_carveouts",
            "text": "Confidential Information does not include information that (a) becomes publicly available through no fault of the receiving party, (b) was in the receiving party's possession without restriction before disclosure, (c) is independently developed without use of Confidential Information, or (d) is rightfully received from a third party without restriction. Compelled disclosure requires prompt notice to allow protective measures.",
            "risk_score": 15,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "Chaque partie s'engage a maintenir la confidentialite des informations de l'autre partie en utilisant au minimum le meme degre de protection que celui applique a ses propres informations confidentielles. Les obligations de confidentialite perdurent pendant trois ans apres la fin du contrat.",
            "risk_score": 18,
            "jurisdiction": "FR",
        },
    ],
    "intellectual_property": [
        {
            "level": "balanced",
            "text": "Each party retains all right, title, and interest in its pre-existing intellectual property. Any intellectual property developed jointly shall be jointly owned. Provider grants Client a non-exclusive, worldwide, royalty-free license to use deliverables for Client's internal business purposes. Neither party acquires rights to the other's intellectual property except as expressly stated herein.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "client_favorable",
            "text": "All work product, deliverables, and materials created by Provider specifically for Client under this Agreement shall be considered works made for hire and shall be the exclusive property of Client. Provider assigns all rights therein to Client. Provider retains rights to its pre-existing tools and methodologies, granting Client a perpetual license thereto.",
            "risk_score": 30,
            "jurisdiction": "general",
        },
        {
            "level": "provider_favorable",
            "text": "Provider retains all intellectual property rights in the Services, software, and deliverables. Client receives a non-exclusive, non-transferable license to use the deliverables during the term of this Agreement. Upon termination, Client's license terminates and Client shall cease all use.",
            "risk_score": 35,
            "jurisdiction": "general",
        },
        {
            "level": "standard",
            "text": "Background IP remains with the originating party. Foreground IP developed under this Agreement is owned by the party whose resources primarily contributed to its creation. Each party grants the other a non-exclusive license to use Foreground IP for purposes of this Agreement.",
            "risk_score": 22,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "Chaque partie conserve la propriete de sa propriete intellectuelle preexistante. Les creations realisees conjointement sont en copropriete. Le Prestataire concede au Client une licence non exclusive pour l'utilisation des livrables dans le cadre de ses activites.",
            "risk_score": 22,
            "jurisdiction": "FR",
        },
    ],
    "governing_law": [
        {
            "level": "balanced",
            "text": "This Agreement shall be governed by and construed in accordance with the laws of [State/Country], without regard to conflict of law principles. Any disputes shall be submitted to the exclusive jurisdiction of the courts of [City], [State/Country]. Each party irrevocably consents to such jurisdiction.",
            "risk_score": 15,
            "jurisdiction": "general",
        },
        {
            "level": "with_arbitration",
            "text": "This Agreement is governed by the laws of [Jurisdiction]. Any dispute arising under this Agreement shall be resolved by binding arbitration under the rules of [Institution] before a single arbitrator in [City]. The arbitrator's decision shall be final and enforceable in any court of competent jurisdiction. Each party bears its own costs.",
            "risk_score": 18,
            "jurisdiction": "general",
        },
        {
            "level": "standard",
            "text": "This Agreement shall be governed by the laws of the jurisdiction specified in the Order Form. The parties consent to exclusive jurisdiction and venue in the courts located in that jurisdiction for any dispute not subject to arbitration.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "multi_jurisdiction",
            "text": "This Agreement shall be governed by the laws of [Primary Jurisdiction]. For disputes involving amounts under $500,000, resolution shall be by mediation followed by binding arbitration. For larger disputes, each party may seek relief in courts of competent jurisdiction.",
            "risk_score": 22,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "Le present contrat est regi par le droit francais. Tout differend sera soumis a la competence exclusive des tribunaux de Paris, sauf accord contraire des parties pour un recours a la mediation ou l'arbitrage.",
            "risk_score": 15,
            "jurisdiction": "FR",
        },
    ],
    "data_protection": [
        {
            "level": "balanced",
            "text": "Each party shall comply with applicable data protection laws, including GDPR where applicable. Provider shall process personal data only as instructed by Client and shall implement appropriate technical and organizational measures. Provider shall notify Client of any data breach without undue delay, and in any event within seventy-two (72) hours. Data processing details are set forth in the Data Processing Agreement attached hereto.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "protective",
            "text": "Provider acts as data processor on behalf of Client (data controller). Provider shall: (a) process personal data only on Client's documented instructions; (b) ensure personnel are bound by confidentiality; (c) implement security measures per Article 32 GDPR; (d) assist with data subject rights requests; (e) delete or return all personal data upon termination; (f) submit to audits. Sub-processors require Client's prior written consent.",
            "risk_score": 15,
            "jurisdiction": "EU",
        },
        {
            "level": "standard",
            "text": "Provider shall maintain industry-standard security measures to protect personal data. Provider shall comply with all applicable privacy laws in its performance under this Agreement. In the event of a security incident affecting Client data, Provider shall notify Client promptly and cooperate in any investigation or remediation.",
            "risk_score": 25,
            "jurisdiction": "general",
        },
        {
            "level": "minimal",
            "text": "The parties acknowledge their respective obligations under applicable data protection legislation and agree to cooperate in good faith to ensure compliance. Each party is responsible for its own compliance with data protection laws.",
            "risk_score": 35,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "Les parties s'engagent a respecter la reglementation applicable en matiere de protection des donnees, notamment le RGPD. Le sous-traitant ne traite les donnees personnelles que sur instruction documentee du responsable de traitement et met en oeuvre les mesures de securite appropriees.",
            "risk_score": 18,
            "jurisdiction": "FR",
        },
    ],
    "warranty": [
        {
            "level": "balanced",
            "text": "Provider warrants that the Services will be performed in a professional and workmanlike manner consistent with generally accepted industry standards. If Services fail to conform to this warranty, Provider shall, at its option, re-perform the non-conforming Services or refund the fees attributable to such Services. This constitutes Client's sole remedy for breach of this warranty.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "standard",
            "text": "Each party represents and warrants that (a) it has authority to enter into this Agreement, (b) its performance will not violate any other agreement, and (c) it will comply with all applicable laws. EXCEPT AS EXPRESSLY SET FORTH HEREIN, ALL WARRANTIES ARE DISCLAIMED, INCLUDING IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.",
            "risk_score": 30,
            "jurisdiction": "general",
        },
        {
            "level": "protective",
            "text": "Provider warrants that: (a) Services will conform to specifications for ninety (90) days after delivery; (b) deliverables will not infringe third-party IP rights; (c) Services will comply with applicable laws. Provider shall promptly correct any non-conformance at no additional charge.",
            "risk_score": 18,
            "jurisdiction": "general",
        },
        {
            "level": "with_sla",
            "text": "Provider warrants 99.9% uptime for hosted services, measured monthly. If uptime falls below the warranted level, Client is entitled to service credits as specified in the SLA. Service credits are Client's sole and exclusive remedy for downtime.",
            "risk_score": 22,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "Le Prestataire garantit que les Services seront executes avec le soin et la diligence d'un professionnel competent. En cas de non-conformite, le Prestataire s'engage a reprendre les Services defaillants sans frais supplementaires dans un delai raisonnable.",
            "risk_score": 20,
            "jurisdiction": "FR",
        },
    ],
    "payment_terms": [
        {
            "level": "balanced",
            "text": "Client shall pay all invoices within thirty (30) days of receipt. Late payments accrue interest at the lesser of 1.5% per month or the maximum rate permitted by law. Provider may suspend Services upon fifteen (15) days' written notice of non-payment, provided Client has not disputed the invoice in good faith. Disputed amounts shall be resolved through good-faith discussion.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "standard",
            "text": "All fees are due net thirty (30) days from invoice date. Fees are exclusive of taxes, which Client shall pay. Provider may increase fees annually upon sixty (60) days' notice, with increases not exceeding the greater of 5% or the applicable consumer price index change.",
            "risk_score": 25,
            "jurisdiction": "general",
        },
        {
            "level": "protective",
            "text": "Fees are fixed for the initial term. Payment is due within forty-five (45) days of receipt of a properly submitted invoice. Client may withhold payment of genuinely disputed amounts pending resolution, without incurring late fees. Provider shall not suspend Services for disputed amounts.",
            "risk_score": 18,
            "jurisdiction": "general",
        },
        {
            "level": "milestone",
            "text": "Fees shall be paid upon achievement of milestones as defined in the Statement of Work. Each milestone payment is contingent upon Client's written acceptance of the corresponding deliverable. Final payment is due upon completion and acceptance of all deliverables.",
            "risk_score": 22,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "Les factures sont payables dans un delai de trente jours a compter de leur reception. Les retards de paiement entrainent de plein droit des penalites de retard au taux legal en vigueur, ainsi qu'une indemnite forfaitaire de 40 euros pour frais de recouvrement.",
            "risk_score": 20,
            "jurisdiction": "FR",
        },
    ],
    "non_compete": [
        {
            "level": "balanced",
            "text": "During the term and for twelve (12) months thereafter, neither party shall directly solicit for employment any employee of the other party who was materially involved in the performance of this Agreement, without prior written consent. This restriction does not apply to general recruitment efforts not targeted at the other party's employees.",
            "risk_score": 25,
            "jurisdiction": "general",
        },
        {
            "level": "narrow",
            "text": "Employee non-solicitation: For twelve months after termination, neither party shall directly recruit employees who worked on this engagement. Customer non-solicitation: Provider shall not solicit Client's customers using confidential information obtained under this Agreement.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "standard",
            "text": "During the term and for a period of one (1) year after expiration or termination, the parties agree not to directly or indirectly solicit, recruit, or hire any employee of the other party who was involved in the performance of this Agreement.",
            "risk_score": 28,
            "jurisdiction": "general",
        },
        {
            "level": "limited",
            "text": "The non-solicitation obligation is limited to direct, targeted solicitation and does not restrict either party from hiring individuals who respond to general job postings or who independently seek employment.",
            "risk_score": 18,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "Pendant la duree du contrat et pendant douze mois apres son terme, les parties s'engagent a ne pas solliciter directement les employes de l'autre partie ayant participe a l'execution du contrat, sauf accord ecrit prealable.",
            "risk_score": 25,
            "jurisdiction": "FR",
        },
    ],
    "dispute_resolution": [
        {
            "level": "balanced",
            "text": "The parties shall attempt to resolve any dispute through good-faith negotiation for thirty (30) days. If unresolved, the dispute shall be submitted to mediation under the rules of [Institution]. If mediation fails within sixty (60) days, either party may pursue binding arbitration or litigation as provided herein.",
            "risk_score": 15,
            "jurisdiction": "general",
        },
        {
            "level": "escalation",
            "text": "Disputes shall be escalated as follows: (1) project managers for fifteen (15) days; (2) senior executives for fifteen (15) days; (3) mediation for thirty (30) days; (4) binding arbitration before a single arbitrator. Each party bears its own costs through mediation; arbitration costs are shared equally.",
            "risk_score": 18,
            "jurisdiction": "general",
        },
        {
            "level": "standard",
            "text": "Any dispute arising under or relating to this Agreement shall be resolved by binding arbitration in accordance with the rules of the American Arbitration Association (or equivalent). The arbitration shall take place in [City], and the decision shall be final and binding.",
            "risk_score": 22,
            "jurisdiction": "US",
        },
        {
            "level": "litigation",
            "text": "Any dispute arising under this Agreement shall be submitted to the exclusive jurisdiction of the courts of [Jurisdiction]. Each party waives any objection to venue. The prevailing party shall be entitled to recover its reasonable attorneys' fees and costs.",
            "risk_score": 25,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "En cas de differend, les parties s'engagent a rechercher une solution amiable pendant trente jours. A defaut d'accord, le differend sera soumis a la mediation. En cas d'echec de la mediation, les tribunaux competents de Paris seront saisis.",
            "risk_score": 18,
            "jurisdiction": "FR",
        },
    ],
    "insurance": [
        {
            "level": "balanced",
            "text": "Provider shall maintain the following insurance during the term and for two (2) years thereafter: (a) commercial general liability of at least $1,000,000 per occurrence; (b) professional errors and omissions of at least $2,000,000 per claim; (c) cyber liability of at least $5,000,000 per claim. Provider shall furnish certificates of insurance upon request.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "standard",
            "text": "Each party shall maintain insurance coverage appropriate to its obligations under this Agreement, including commercial general liability and professional liability insurance. Evidence of coverage shall be provided upon written request.",
            "risk_score": 25,
            "jurisdiction": "general",
        },
        {
            "level": "detailed",
            "text": "Provider shall maintain: general liability ($2M), professional liability ($5M), workers' compensation (statutory limits), and cyber/data breach insurance ($5M). Client shall be named as additional insured on CGL policy. Provider shall provide thirty (30) days' notice of cancellation or material change.",
            "risk_score": 18,
            "jurisdiction": "general",
        },
        {
            "level": "minimal",
            "text": "Provider represents that it maintains insurance coverage sufficient to cover its obligations under this Agreement and shall provide proof of insurance upon reasonable request.",
            "risk_score": 35,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "Le Prestataire s'engage a maintenir une assurance responsabilite civile professionnelle couvrant les dommages pouvant resulter de l'execution du contrat, pour un montant minimum de 2 000 000 EUR par sinistre. Les attestations d'assurance seront fournies sur demande.",
            "risk_score": 20,
            "jurisdiction": "FR",
        },
    ],
    "audit_rights": [
        {
            "level": "balanced",
            "text": "Client may audit Provider's compliance with this Agreement upon thirty (30) days' prior written notice, no more than once per calendar year, during normal business hours. Audits shall be conducted by Client or a mutually agreed independent auditor bound by confidentiality. Provider shall cooperate and provide reasonable access to relevant records. Audit costs are borne by Client unless the audit reveals material non-compliance, in which case Provider bears the costs.",
            "risk_score": 18,
            "jurisdiction": "general",
        },
        {
            "level": "standard",
            "text": "Client shall have the right, upon reasonable prior written notice, to audit Provider's books, records, and systems to verify compliance with this Agreement. Audits shall not unreasonably interfere with Provider's business operations.",
            "risk_score": 22,
            "jurisdiction": "general",
        },
        {
            "level": "comprehensive",
            "text": "Client may conduct audits of Provider's compliance, security controls, and data handling practices. Provider shall maintain complete and accurate records for the duration of the Agreement and for three (3) years thereafter. Provider shall promptly remediate any findings of non-compliance.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "limited",
            "text": "Provider shall provide Client with annual SOC 2 Type II reports and any additional compliance certifications as reasonably requested. Client may request an independent third-party audit at Client's expense if SOC 2 reports reveal material concerns.",
            "risk_score": 25,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "Le Client dispose d' un droit d'audit annuel, exercable moyennant un preavis de trente jours, pour verifier la conformite du Prestataire. L'audit est realise aux frais du Client, sauf en cas de non-conformite significative constatee.",
            "risk_score": 20,
            "jurisdiction": "FR",
        },
    ],
    "force_majeure": [
        {
            "level": "balanced",
            "text": "Neither party shall be liable for failure to perform its obligations due to events beyond its reasonable control, including natural disasters, war, terrorism, pandemics, government actions, labor disputes, and infrastructure failures. The affected party shall provide prompt notice, use commercially reasonable efforts to mitigate, and resume performance as soon as practicable. If the force majeure event continues for more than ninety (90) days, either party may terminate without liability.",
            "risk_score": 15,
            "jurisdiction": "general",
        },
        {
            "level": "standard",
            "text": "Neither party is liable for delays or failures to perform caused by circumstances beyond its reasonable control. The affected party must notify the other party promptly and take reasonable steps to minimize the impact. Payment obligations are not excused by force majeure.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "detailed",
            "text": "Force majeure events include but are not limited to: natural disasters, epidemics, cyber attacks, governmental orders, sanctions, energy failures, and telecommunications outages. The affected party must notify within five (5) business days. Performance obligations are suspended for the duration. If suspension exceeds sixty (60) days, either party may terminate the affected work order.",
            "risk_score": 18,
            "jurisdiction": "general",
        },
        {
            "level": "protective",
            "text": "Force majeure events excuse delayed performance but do not excuse payment obligations or data protection obligations. The affected party shall implement its business continuity plan and provide weekly updates on expected resumption. Client may procure alternative services during the force majeure event without breach.",
            "risk_score": 22,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "Aucune partie ne sera responsable en cas d'inexecution due a un cas de force majeure tel que defini par l'article 1218 du Code civil. La partie affectee devra notifier l'autre partie dans les cinq jours et prendre les mesures raisonnables pour limiter les effets. Si l'evenement persiste au-dela de quatre-vingt-dix jours, chaque partie pourra resilier sans indemnite.",
            "risk_score": 15,
            "jurisdiction": "FR",
        },
    ],
    "scope_of_work": [
        {
            "level": "balanced",
            "text": "The Services are defined in the Statement of Work attached hereto. Any changes to scope require a written change order signed by both parties, specifying the impact on timeline, fees, and deliverables. Provider shall not perform out-of-scope work without prior written authorization. Provider shall promptly notify Client if it becomes aware that additional work may be required.",
            "risk_score": 18,
            "jurisdiction": "general",
        },
        {
            "level": "standard",
            "text": "Provider shall perform the Services described in each Statement of Work executed under this Agreement. The scope, timeline, and fees are as set forth in the applicable Statement of Work. Changes require mutual written agreement.",
            "risk_score": 22,
            "jurisdiction": "general",
        },
        {
            "level": "protective",
            "text": "The scope of Services is strictly limited to the deliverables described in the Statement of Work. Provider's obligation to perform is conditioned upon Client's timely provision of required access, information, and approvals. Delays caused by Client shall extend timelines accordingly.",
            "risk_score": 20,
            "jurisdiction": "general",
        },
        {
            "level": "agile",
            "text": "Services shall be delivered in iterative sprints as agreed by the parties. Scope is managed through a prioritized backlog, with adjustments permitted at sprint boundaries. Total fees shall not exceed the agreed budget without Client's written approval.",
            "risk_score": 25,
            "jurisdiction": "general",
        },
        {
            "level": "fr_balanced",
            "text": "Les Services sont definis dans le cahier des charges annexe. Toute modification du perimetre necessite un avenant ecrit signe par les deux parties, precisant l'impact sur les delais et les couts. Le Prestataire ne pourra effectuer de travaux hors perimetre sans accord ecrit prealable.",
            "risk_score": 18,
            "jurisdiction": "FR",
        },
    ],
}


# ==================== REWRITE ENGINE ====================

@dataclass
class RewriteSuggestion:
    """A suggested clause rewrite."""
    original_text: str
    suggested_text: str
    clause_type: str
    original_risk_score: float  # estimated from dispute probability
    suggested_risk_score: float
    risk_reduction: float  # percentage points reduced
    template_level: str  # "balanced", "protective", etc.
    similarity_to_original: float  # cosine sim between original and suggestion
    explanation: str
    diff_summary: str  # human-readable diff

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clause_type": self.clause_type,
            "original_preview": self.original_text[:200] + "..." if len(self.original_text) > 200 else self.original_text,
            "suggested_text": self.suggested_text,
            "original_risk": round(self.original_risk_score, 1),
            "suggested_risk": round(self.suggested_risk_score, 1),
            "risk_reduction": round(self.risk_reduction, 1),
            "template_level": self.template_level,
            "similarity": round(self.similarity_to_original, 3),
            "explanation": self.explanation,
            "diff_summary": self.diff_summary,
        }


class RewriteEngine:
    """
    Suggests safer clause alternatives using contrastive embedding search.
    
    How it works:
    1. Pre-embeds all safe clause templates at init
    2. When a risky clause is detected, encodes it 
    3. Finds the nearest safe template via cosine similarity
    4. Returns a RewriteSuggestion with diff and risk delta
    
    Uses the SAME encoder as the classifier — zero additional cost.
    """

    def __init__(self, encoder=None):
        """
        Initialize with a sentence encoder.
        If none provided, will import and use the classifier's encoder.
        """
        self._encoder = encoder
        self._template_embeddings: Dict[str, np.ndarray] = {}
        self._template_metadata: Dict[str, List[Dict]] = {}
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization to avoid loading model if not needed."""
        if self._initialized:
            return

        if self._encoder is None:
            from src.v10.classifier_v10 import get_classifier
            classifier = get_classifier(multilingual=True)
            self._encoder = classifier.model

        # Pre-embed all templates
        for clause_type, templates in CLAUSE_TEMPLATES.items():
            texts = [t["text"] for t in templates]
            embeddings = self._encoder.encode(
                texts, normalize_embeddings=True, show_progress_bar=False
            )
            self._template_embeddings[clause_type] = embeddings
            self._template_metadata[clause_type] = templates

        self._initialized = True
        logger.info(
            f"RewriteEngine initialized with {sum(len(t) for t in CLAUSE_TEMPLATES.values())} templates "
            f"across {len(CLAUSE_TEMPLATES)} clause types"
        )

    def suggest(
        self,
        clause_text: str,
        clause_type: str,
        current_risk: float = 50.0,
        preferred_level: Optional[str] = None,
    ) -> Optional[RewriteSuggestion]:
        """
        Suggest a safer rewrite for a risky clause.
        
        Args:
            clause_text: The original clause text
            clause_type: The classified clause type
            current_risk: Current dispute probability (0-100)
            preferred_level: Optional preferred template level
            
        Returns:
            RewriteSuggestion or None if no templates available
        """
        self._ensure_initialized()

        if clause_type not in self._template_embeddings:
            logger.warning(f"No templates for clause type: {clause_type}")
            return None

        # Encode the original clause
        clause_embedding = self._encoder.encode(
            [clause_text], normalize_embeddings=True, show_progress_bar=False
        )[0]

        # Find best matching template
        template_embeddings = self._template_embeddings[clause_type]
        templates = self._template_metadata[clause_type]

        # Cosine similarities
        similarities = np.dot(template_embeddings, clause_embedding)

        # Score = balance of similarity (want similar style) and low risk
        best_idx = None
        best_score = -1

        for i, (sim, template) in enumerate(zip(similarities, templates)):
            # Skip if preferred_level specified and doesn't match
            if preferred_level and template["level"] != preferred_level:
                continue

            # Only suggest templates with LOWER risk
            if template["risk_score"] >= current_risk:
                continue

            # Score: weighted combo of similarity and risk reduction
            risk_reduction = current_risk - template["risk_score"]
            score = sim * 0.4 + (risk_reduction / 100) * 0.6

            if score > best_score:
                best_score = score
                best_idx = i

        if best_idx is None:
            # Fall back: find the lowest-risk template regardless
            sorted_by_risk = sorted(enumerate(templates), key=lambda x: x[1]["risk_score"])
            for i, t in sorted_by_risk:
                if t["risk_score"] < current_risk:
                    best_idx = i
                    break

        if best_idx is None:
            return None

        best_template = templates[best_idx]
        similarity = float(similarities[best_idx])
        risk_reduction = current_risk - best_template["risk_score"]

        # Generate diff summary
        diff_summary = self._generate_diff_summary(clause_text, best_template["text"])

        # Generate explanation
        explanation = self._generate_explanation(
            clause_type, best_template["level"], risk_reduction, similarity
        )

        return RewriteSuggestion(
            original_text=clause_text,
            suggested_text=best_template["text"],
            clause_type=clause_type,
            original_risk_score=current_risk,
            suggested_risk_score=best_template["risk_score"],
            risk_reduction=risk_reduction,
            template_level=best_template["level"],
            similarity_to_original=similarity,
            explanation=explanation,
            diff_summary=diff_summary,
        )

    def suggest_batch(
        self,
        clauses: List[Dict[str, Any]],
        risk_threshold: float = 40.0,
    ) -> List[RewriteSuggestion]:
        """
        Suggest rewrites for all high-risk clauses.
        
        Args:
            clauses: List of classified clauses with dispute probabilities
            risk_threshold: Only suggest rewrites for clauses above this risk
        """
        self._ensure_initialized()
        suggestions = []

        for clause in clauses:
            risk = clause.get("dispute_probability", 0) * 100
            if risk < risk_threshold:
                continue

            suggestion = self.suggest(
                clause_text=clause.get("text", ""),
                clause_type=clause.get("clause_type", ""),
                current_risk=risk,
            )
            if suggestion:
                suggestions.append(suggestion)

        return sorted(suggestions, key=lambda s: s.risk_reduction, reverse=True)

    def _generate_diff_summary(self, original: str, suggested: str) -> str:
        """Generate a human-readable diff summary."""
        orig_words = original.lower().split()
        sugg_words = suggested.lower().split()

        matcher = difflib.SequenceMatcher(None, orig_words, sugg_words)
        ratio = matcher.ratio()

        # Key differences
        additions = []
        removals = []
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == "insert":
                phrase = " ".join(sugg_words[j1:j2])
                if len(phrase) > 10:
                    additions.append(phrase[:60])
            elif op == "delete":
                phrase = " ".join(orig_words[i1:i2])
                if len(phrase) > 10:
                    removals.append(phrase[:60])
            elif op == "replace":
                old = " ".join(orig_words[i1:i2])
                new = " ".join(sugg_words[j1:j2])
                if len(old) > 10:
                    removals.append(old[:60])
                if len(new) > 10:
                    additions.append(new[:60])

        parts = []
        if removals:
            parts.append(f"Removes: {'; '.join(removals[:3])}")
        if additions:
            parts.append(f"Adds: {'; '.join(additions[:3])}")
        parts.append(f"Text similarity: {ratio:.0%}")
        return " | ".join(parts)

    def _generate_explanation(
        self, clause_type: str, level: str, risk_reduction: float, similarity: float
    ) -> str:
        """Generate a natural language explanation."""
        type_name = clause_type.replace("_", " ")

        explanations = {
            "balanced": f"Replace with a mutual, balanced {type_name} clause that distributes obligations equally between parties.",
            "protective": f"Replace with a more protective {type_name} clause that adds safeguards and explicit carve-outs.",
            "standard": f"Replace with industry-standard {type_name} language that follows commercial best practices.",
            "mutual": f"Replace with a mutual {type_name} clause where both parties share equivalent obligations.",
            "tiered": f"Replace with a tiered {type_name} structure that proportions liability to severity.",
            "with_arbitration": f"Replace with a {type_name} clause that includes structured dispute resolution via arbitration.",
            "escalation": f"Replace with a multi-tier {type_name} mechanism: negotiation, then mediation, then arbitration.",
            "narrow": f"Replace with a narrowly scoped {type_name} clause that limits restrictions to targeted activities.",
            "limited": f"Replace with a limited {type_name} clause that provides reasonable boundaries.",
        }

        base = explanations.get(level, f"Replace with a {level} {type_name} clause.")
        return f"{base} Estimated risk reduction: {risk_reduction:.0f} points."


__all__ = ["RewriteEngine", "RewriteSuggestion", "CLAUSE_TEMPLATES"]

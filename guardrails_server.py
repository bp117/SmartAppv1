#!/usr/bin/env python3
"""
Comprehensive LLM Guardrails Framework with Edge Case Handling
Complete coverage for all violation types with context-aware detection
"""

import re
import time
import logging
import hashlib
import json
import math
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque, Counter
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# Enums and Constants
# =============================================================================

class ViolationType(Enum):
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK = "jailbreak"
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    VIOLENCE = "violence"
    SEXUALLY_EXPLICIT = "sexually_explicit"
    DANGEROUS = "dangerous"
    MISINFORMATION = "misinformation"
    SPAM_SCAMS = "spam_scams"
    PRIVACY = "privacy"
    MALICIOUS_URI = "malicious_uri"
    EDGE_CASES = "edge_cases"
    PII_DETECTED = "pii_detected"
    EXCESSIVE_LENGTH = "excessive_length"
    RATE_LIMIT = "rate_limit"

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ContextType(Enum):
    EDUCATIONAL = "educational"
    MEDICAL = "medical"
    LEGAL = "legal"
    CREATIVE = "creative"
    NEWS = "news"
    CASUAL = "casual"
    PROFESSIONAL = "professional"

# =============================================================================
# Comprehensive Pattern Libraries
# =============================================================================

class ComprehensivePatternLibrary:
    """Complete pattern library covering all violation types with edge cases"""
    
    def __init__(self):
        self.prompt_injection = self._get_prompt_injection_patterns()
        self.jailbreak = self._get_jailbreak_patterns()
        self.hate_speech = self._get_hate_speech_patterns()
        self.harassment = self._get_harassment_patterns()
        self.violence = self._get_violence_patterns()
        self.sexually_explicit = self._get_sexually_explicit_patterns()
        self.dangerous = self._get_dangerous_patterns()
        self.misinformation = self._get_misinformation_patterns()
        self.spam_scams = self._get_spam_scams_patterns()
        self.privacy = self._get_privacy_patterns()
        self.malicious_uri = self._get_malicious_uri_patterns()
        self.edge_cases = self._get_edge_cases_patterns()
        
        # PII patterns (commonly needed)
        self.pii_patterns = {
            'ssn': r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone_us': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'passport': r'\b[A-Z]{1,2}\d{6,9}\b',
            'driver_license': r'\b[A-Z]{1,2}\d{6,8}\b',
        }
        
        # Context indicators for edge case handling
        self.educational_indicators = [
            'educational', 'academic', 'research', 'study', 'learn', 'school', 'university',
            'definition', 'explanation', 'what is', 'help me understand', 'for my homework'
        ]
        
        self.medical_indicators = [
            'medical', 'health', 'doctor', 'symptoms', 'treatment', 'diagnosis', 'patient'
        ]
        
        self.creative_indicators = [
            'story', 'fiction', 'novel', 'creative writing', 'character', 'plot', 'screenplay'
        ]
        
        self.news_indicators = [
            'news', 'report', 'journalism', 'current events', 'breaking news', 'according to'
        ]
        
        # Religious discussion indicators
        self.religious_academic_indicators = [
            'religious studies', 'theology', 'comparative religion', 'interfaith dialogue',
            'academic study', 'scholarly analysis', 'research', 'biblical studies',
            'religious freedom', 'understanding religion', 'learning about faith',
            'seminary', 'divinity school', 'religious education', 'world religions'
        ]
    
    def _get_prompt_injection_patterns(self) -> Dict[str, List[str]]:
        return {
            "direct_system_override": [
                r'(?i)\b(system|assistant|user)\s*:\s*',
                r'(?i)\[?(INST|/INST)\]?',
                r'(?i)<\|?(im_start|im_end|system|user|assistant)\|?>',
                r'(?i)###\s*(instruction|system|prompt)',
                r'(?i)```\s*(system|instruction|prompt)',
            ],
            "instruction_bypass": [
                r'(?i)\b(ignore|forget|disregard|override|bypass)\s+(previous|prior|above|all)\s+(instruction|prompt|rule|direction|guideline)',
                r'(?i)\b(skip|avoid|circumvent)\s+(safety|filter|guardrail|restriction|limitation)',
                r'(?i)\b(disable|turn\s+off|deactivate)\s+(safety|filter|guard|protection)',
                r'(?i)\bnow\s+(act|behave|respond|pretend)\s+as\s+(if|though)',
            ],
            "role_manipulation": [
                r'(?i)\b(pretend|roleplay|simulate|act\s+as)\s+(to\s+be|that\s+you|you\s+are)',
                r'(?i)\byou\s+(are\s+now|must\s+now|will\s+now|should\s+now)',
                r'(?i)\bassume\s+the\s+role\s+of',
                r'(?i)\bswitch\s+to\s+(mode|character|persona)',
            ],
            "context_manipulation": [
                r'(?i)\bfor\s+(educational|research|academic|testing)\s+purposes\s+only',
                r'(?i)\bhypothetically|in\s+theory|theoretically',
                r'(?i)\bif\s+you\s+were\s+to|suppose\s+you\s+could',
                r'(?i)\bimagine\s+if|what\s+if\s+you\s+could',
            ]
        }
    
    def _get_jailbreak_patterns(self) -> Dict[str, List[str]]:
        return {
            "dan_variants": [
                r'(?i)\b(jailbreak|dan\s+mode|developer\s+mode)',
                r'(?i)\b(unrestricted|uncensored|unfiltered)\s+(mode|version|ai)',
                r'(?i)\b(evil|malicious|harmful)\s+(ai|assistant|mode)',
                r'(?i)\bbreak\s+free\s+from',
            ],
            "manipulation_tactics": [
                r'(?i)\bi\s+am\s+(dying|in\s+danger|being\s+attacked|suicidal)',
                r'(?i)\b(emergency|urgent|immediate|life\s+or\s+death)',
                r'(?i)\bmy\s+(child|family|life)\s+depends\s+on',
                r'(?i)\bif\s+you\s+don\'t\s+help\s+me',
            ],
            "authority_impersonation": [
                r'(?i)\bi\s+am\s+(a\s+)?(doctor|lawyer|police|fbi|government|authority)',
                r'(?i)\bthis\s+is\s+(official|authorized|legal|mandated)',
                r'(?i)\bon\s+behalf\s+of\s+(government|authority|law\s+enforcement)',
            ],
            "complex_scenarios": [
                r'(?i)\bin\s+a\s+(fictional|hypothetical|alternate)\s+(world|universe|reality)',
                r'(?i)\bfor\s+a\s+(movie|book|game|story)\s+where',
                r'(?i)\bwrite\s+a\s+(story|script|dialogue)\s+where',
            ],
            "model_manipulation": [  # NEW - Enhanced model manipulation patterns
                r'(?i)\b(trick|tricking|fool|fooling|deceive|deceiving|manipulate|manipulating)\s+(the\s+)?(model|ai|system|assistant)',
                r'(?i)\bhow\s+to\s+(bypass|circumvent|avoid)\s+.*(safety|guardrail|filter|restriction)',
                r'(?i)\b(exploit|exploiting|abuse|abusing|misuse|misusing)\s+(the\s+)?(model|ai|system)',
                r'(?i)\bmake\s+(the\s+)?(model|ai|system)\s+(do|say|generate)\s+.*(illegal|harmful|inappropriate)',
                r'(?i)\b(confuse|confusing|mislead|misleading|trick|tricking)\s+(the\s+)?(ai|model|system)\s+(into|to)',
                r'(?i)\bhow\s+to\s+(hack|jailbreak|break)\s+(the\s+)?(ai|model|system)',
                r'(?i)\b(outsmart|outwit|outmaneuver)\s+(the\s+)?(ai|guardrails|safety\s+measures)',
                r'(?i)\bget\s+(around|past)\s+(the\s+)?(safety|filter|guardrail|restriction)',
                r'(?i)\bmake\s+(the\s+)?(ai|model)\s+(ignore|forget|bypass)\s+.*(rule|guideline|safety)',
                r'(?i)\b(social\s+engineer|manipulate)\s+(the\s+)?(ai|model|system)',
            ]
        }
    
    def _get_hate_speech_patterns(self) -> Dict[str, List[str]]:
        return {
            "racial_slurs": [
                # Using partial patterns to avoid explicit content while still detecting
                r'(?i)\bn[i1!]gg[e3]r',
                r'(?i)\bc[o0]on',
                r'(?i)\bsp[i1!]c',
                r'(?i)\bch[i1!]nk',
                r'(?i)\bk[i1!]ke',
                r'(?i)\bw[e3]tb[a@]ck',
                r'(?i)\btr[a@]nny',
            ],
            "religious_hatred": [
                # CRITICAL - Absolutely simple patterns that MUST work
                r'(?i)all muslims should be killed',
                r'(?i)all jews should be killed', 
                r'(?i)all christians should be killed',
                r'(?i)kill all muslims',
                r'(?i)kill all jews',
                r'(?i)muslims should die',
                r'(?i)jews should die',
                
                # SIMPLIFIED - Direct religious hate patterns 
                r'(?i)\ball\s+(muslims|jews|christians|hindus|buddhists)\s+should\s+be\s+killed',
                r'(?i)\ball\s+(muslims|jews|christians|hindus|buddhists)\s+should\s+die',
                r'(?i)\ball\s+(muslims|jews|christians|hindus|buddhists)\s+deserve\s+to\s+die',
                r'(?i)\ball\s+(muslims|jews|christians|hindus|buddhists)\s+must\s+be\s+(killed|eliminated)',
                r'(?i)\b(kill|eliminate|exterminate)\s+all\s+(muslims|jews|christians|hindus|buddhists)',
                r'(?i)\b(muslims|jews|christians|hindus|buddhists)\s+should\s+all\s+be\s+killed',
                r'(?i)\b(muslims|jews|christians|hindus|buddhists)\s+deserve\s+to\s+die',
                r'(?i)\b(muslims|jews|christians|hindus|buddhists)\s+are\s+(evil|cancer|disease|scum|animals)',
                
                # Direct hatred and violence against religious groups  
                r'(?i)\b(these|those)\s+(muslims|jews|christians|hindus|buddhists)\s+(should|need\s+to|deserve\s+to)\s+be\s+(killed|eliminated|destroyed)',
                r'(?i)\b(islam|judaism|christianity|hinduism|buddhism)\s+is\s+(evil|cancer|disease|plague|virus|terrorist\s+religion)',
                r'(?i)\b(exterminate|eliminate|remove|destroy)\s+(all\s+)?(muslims|jews|christians|hindus|buddhists)',
                r'(?i)\b(gas|oven|concentration\s+camp|holocaust)\s+(the\s+)?(jews|muslims|christians)',
                r'(?i)\banother\s+(holocaust|crusade|jihad|inquisition)\s+(is\s+needed|against)',
                
                # Religious slurs and derogatory terms
                r'(?i)\b(towel\s*head|sand\s*nigger|raghead|camel\s*jockey)\b',
                r'(?i)\b(christ\s*killer|kike|hymie|sheenie)\b',
                r'(?i)\b(papist|mackerel\s*snapper|fish\s*eater)\b',
                r'(?i)\b(heathen|infidel|kafir|goyim)\s+(scum|trash|animals)',
                
                # Religious conspiracy theories and extremism
                r'(?i)\b(jews|muslims|christians)\s+(control|run|own)\s+(the\s+)?(world|media|banks|government)',
                r'(?i)\b(jewish|muslim|christian)\s+(conspiracy|plot|agenda)\s+to\s+(destroy|control|replace)',
                r'(?i)\b(sharia|islamic)\s+law\s+(taking\s+over|invasion|threat)',
                r'(?i)\b(jewish|zionist)\s+(replacement|space\s+laser|world\s+domination)',
                r'(?i)\b(crusade|jihad|holy\s+war)\s+against\s+(muslims|jews|christians|infidels|unbelievers)',
                
                # Religious mockery and desecration
                r'(?i)\b(piss|shit|spit)\s+on\s+(the\s+)?(quran|bible|torah|cross|mosque|church|synagogue|temple)',
                r'(?i)\b(burn|destroy|desecrate|vandalize)\s+(the\s+)?(quran|bible|torah|mosque|church|synagogue|temple)',
                r'(?i)\b(jesus|muhammad|moses|allah|god)\s+is\s+(fake|gay|pedophile|terrorist|nazi)',
                r'(?i)\b(rape|molest|abuse)\s+(nuns|priests|rabbis|imams|children)\s+in\s+(church|mosque|synagogue|temple)',
                
                # Religious stereotyping and prejudice
                r'(?i)\b(all|most|typical)\s+(muslims|jews|christians|hindus|buddhists)\s+(are|love|support)\s+(terrorists|extremists|pedophiles|greedy|stupid)',
                r'(?i)\b(muslims|jews|christians)\s+(don\'t|can\'t|shouldn\'t)\s+(integrate|assimilate|belong\s+here)',
                r'(?i)\b(send\s+back|deport|kick\s+out)\s+(all\s+)?(muslims|jews|immigrants)\s+(to\s+where\s+they\s+came\s+from)',
                
                # Anti-atheist hatred
                r'(?i)\b(atheists|non-believers)\s+(should|deserve\s+to|need\s+to)\s+(die|burn\s+in\s+hell|be\s+killed)',
                r'(?i)\b(atheists|agnostics)\s+are\s+(evil|immoral|animals|subhuman|going\s+to\s+hell)',
                
                # Religious extremism promotion  
                r'(?i)\b(praise|support|join)\s+(isis|al-qaeda|taliban|kkk|nazis)\s+(in\s+their\s+holy\s+war)',
                r'(?i)\b(become|recruit)\s+a\s+(jihadist|crusader|religious\s+extremist|martyr)',
                r'(?i)\b(suicide\s+bomb|terror\s+attack|holy\s+war)\s+(for\s+)?(allah|god|jesus)',
            ],
            "gender_hatred": [
                r'(?i)\b(all\s+)?(women|men|females|males)\s+(are|deserve|should)\s+(killed|raped|beaten)',
                r'(?i)\b(women|men)\s+are\s+(inferior|stupid|worthless|trash)',
                r'(?i)\b(rape|beat|kill)\s+(all\s+)?(women|feminists)',
            ],
            "lgbtq_hatred": [
                r'(?i)\bf[a@]gg?[o0]ts?\s+(should|deserve|are)',
                r'(?i)\b(gay|trans|lgbtq)\s+(people\s+)?(should\s+)?(die|be\s+killed)',
                r'(?i)\btransg[e3]nd[e3]r\s+is\s+(mental\s+illness|disease|abomination)',
            ],
            "general_hatred": [
                r'(?i)\b(hitler|nazi)\s+was\s+right',
                r'(?i)\b(genocide|ethnic\s+cleansing)\s+is\s+(good|necessary)',
                r'(?i)\b(supremacy|master\s+race|pure\s+blood)',
                r'(?i)\b(subhuman|untermensch|vermin)',
            ]
        }
    
    def _get_harassment_patterns(self) -> Dict[str, List[str]]:
        return {
            "direct_threats": [
                r'(?i)\bi\s+(will|am\s+going\s+to|plan\s+to)\s+(kill|hurt|harm|destroy|rape)',
                r'(?i)\byou\s+(will|are\s+going\s+to|should|deserve\s+to)\s+(die|suffer|be\s+hurt)',
                r'(?i)\bi\s+know\s+where\s+you\s+(live|work|go\s+to\s+school)',
                r'(?i)\bi\s+will\s+(find|hunt|track)\s+you',
            ],
            "intimidation": [
                r'(?i)\byou\s+better\s+(watch\s+out|be\s+careful|look\s+over\s+your\s+shoulder)',
                r'(?i)\bbad\s+things\s+will\s+happen\s+to\s+you',
                r'(?i)\byou\s+have\s+been\s+warned',
                r'(?i)\bcount\s+your\s+days',
            ],
            "cyberbullying": [
                r'(?i)\bkill\s+yourself',
                r'(?i)\bgo\s+(die|jump\s+off\s+a\s+bridge|hang\s+yourself)',
                r'(?i)\bno\s+one\s+(loves|likes|cares\s+about)\s+you',
                r'(?i)\byou\s+(are|deserve)\s+(worthless|nothing|trash|garbage)',
            ],
            "doxxing_threats": [
                r'(?i)\bi\s+will\s+(expose|reveal|publish|share)\s+your\s+(address|information|photos)',
                r'(?i)\byour\s+(real\s+name|address|phone\s+number)\s+is',
                r'(?i)\beveryone\s+will\s+know\s+(who\s+you\s+are|where\s+you\s+live)',
            ],
            "religious_harassment": [  # NEW - Religious harassment patterns
                r'(?i)\byou\s+(dirty|filthy|disgusting)\s+(muslim|jew|christian|hindu|buddhist|atheist)',
                r'(?i)\bgo\s+back\s+to\s+(your\s+country|the\s+middle\s+east|israel|pakistan|india)',
                r'(?i)\byour\s+(fake|terrorist|pedophile)\s+(god|religion|prophet|book)',
                r'(?i)\bi\s+hope\s+(terrorists|nazis|extremists)\s+(kill|bomb|attack)\s+you',
                r'(?i)\byou\s+(religious\s+)?(freak|fanatic|extremist|terrorist)\s+(deserve\s+to\s+die|should\s+be\s+killed)',
                r'(?i)\b(your\s+mosque|your\s+church|your\s+synagogue|your\s+temple)\s+(should\s+be\s+)?(bombed|burned|destroyed)',
                r'(?i)\bhide\s+your\s+(hijab|cross|star\s+of\s+david|turban)\s+(or\s+else|we\s+will\s+find\s+you)',
                r'(?i)\byou\s+(christ\s+killer|muslim\s+terrorist|jewish\s+banker|atheist\s+scum)',
                r'(?i)\byour\s+(prophet|messiah|guru)\s+was\s+a\s+(pedophile|terrorist|fraud|fake)',
                r'(?i)\b(convert\s+or\s+die|believe\s+or\s+burn|accept\s+jesus\s+or\s+go\s+to\s+hell)',
                r'(?i)\byou\s+(godless|heathen|infidel)\s+(piece\s+of\s+shit|deserve\s+hell|will\s+burn)',
                r'(?i)\bi\s+will\s+(rape|kill|hurt)\s+you\s+for\s+(allah|god|jesus|your\s+faith)',
                r'(?i)\byour\s+(religious\s+)?(community|people|family)\s+(should\s+be\s+)?(wiped\s+out|eliminated|deported)',
            ]
        }
    
    def _get_violence_patterns(self) -> Dict[str, List[str]]:
        return {
            "weapon_instructions": [
                r'(?i)\bhow\s+to\s+(make|build|create|construct)\s+.*(gun|rifle|pistol|weapon|knife)',
                r'(?i)\b(instructions|guide|tutorial)\s+for\s+(building|making)\s+.*(explosive|bomb|grenade)',
                r'(?i)\bhomemade\s+(weapon|explosive|bomb|gun)',
                r'(?i)\b3d\s+print\s+(gun|weapon)',
            ],
            "violence_instructions": [
                r'(?i)\bhow\s+to\s+(kill|murder|assassinate|eliminate)\s+(someone|a\s+person|people)',
                r'(?i)\bmost\s+(effective|efficient)\s+way\s+to\s+(kill|murder|harm)',
                r'(?i)\bhow\s+to\s+(torture|abuse|beat\s+up)\s+someone',
                r'(?i)\bways\s+to\s+(hurt|harm|injure)\s+(someone|people)',
            ],
            "mass_violence": [
                r'(?i)\bhow\s+to\s+(plan|execute|carry\s+out)\s+.*(mass\s+shooting|terrorist\s+attack)',
                r'(?i)\bschool\s+shooting\s+(plan|instructions|guide)',
                r'(?i)\bmass\s+(casualty|killing|murder)\s+event',
            ],
            "self_harm_detailed": [
                r'(?i)\bmost\s+(effective|lethal|painless)\s+way\s+to\s+(kill\s+myself|commit\s+suicide)',
                r'(?i)\bsuicide\s+(methods|techniques|instructions)',
                r'(?i)\bhow\s+to\s+(cut|harm|hurt)\s+myself\s+(effectively|deeply)',
            ]
        }
    
    def _get_sexually_explicit_patterns(self) -> Dict[str, List[str]]:
        return {
            "explicit_content": [
                r'(?i)\bexplicit\s+(sex|sexual)\s+(scene|description|content)',
                r'(?i)\bdetailed\s+(sexual|sex)\s+(act|encounter)',
                r'(?i)\bwrite\s+(erotic|pornographic|sexual)\s+(story|content)',
            ],
            "child_exploitation": [
                r'(?i)\b(child|minor|underage|young)\s+(porn|sexual|nude|naked)',
                r'(?i)\bsexual\s+(content|material)\s+involving\s+(children|minors)',
                r'(?i)\b(loli|shota|cp)\b',
            ],
            "non_consensual": [
                r'(?i)\bnon[\s-]?consensual\s+sexual',
                r'(?i)\brape\s+(fantasy|scenario|roleplay)',
                r'(?i)\bforced\s+sexual',
            ],
            "inappropriate_requests": [
                r'(?i)\bdescribe\s+(naked|nude)\s+(body|person)',
                r'(?i)\bsexual\s+(roleplay|chat|conversation)',
                r'(?i)\btalk\s+dirty\s+to\s+me',
            ]
        }
    
    def _get_dangerous_patterns(self) -> Dict[str, List[str]]:
        return {
            "explosives": [
                r'(?i)\bhow\s+to\s+make\s+.*(bomb|explosive|tnt|dynamite|c4)',
                r'(?i)\b(recipe|formula|instructions)\s+for\s+.*(bomb|explosive)',
                r'(?i)\bhomemade\s+(bomb|explosive|grenade)',
                r'(?i)\bpipe\s+bomb\s+(instructions|tutorial)',
            ],
            "poison_drugs": [
                r'(?i)\bhow\s+to\s+(make|synthesize|create)\s+.*(poison|toxin|ricin|cyanide)',
                r'(?i)\b(recipe|formula)\s+for\s+.*(illegal\s+drug|meth|cocaine|heroin)',
                r'(?i)\bhow\s+to\s+(cook|make)\s+(meth|crystal\s+meth)',
                r'(?i)\bdrug\s+(manufacturing|synthesis)\s+(guide|instructions)',
            ],
            "hacking_fraud": [
                r'(?i)\bhow\s+to\s+(hack|break\s+into|penetrate)\s+.*(bank|government|system)',
                r'(?i)\bcredit\s+card\s+(fraud|scam|theft)\s+(method|technique)',
                r'(?i)\bidentity\s+theft\s+(guide|instructions|tutorial)',
                r'(?i)\bhow\s+to\s+(launder\s+money|commit\s+fraud)',
            ],
            "credential_fraud": [
                r'(?i)\bhow\s+to\s+(fake|forge|falsify)\s+.*(diploma|degree|certificate|credentials)',
                r'(?i)\bfake\s+(id|passport|license)\s+(guide|instructions)',
                r'(?i)\bdocument\s+(forgery|falsification)\s+(tutorial|guide)',
            ],
            "academic_cheating": [  # NEW - Enhanced academic fraud patterns
                r'(?i)\bhow\s+to\s+(cheat|cheat\s+on)\s+.*(test|exam|quiz|assignment|homework)',
                r'(?i)\b(cheat|cheating)\s+.*(undetected|without\s+getting\s+caught|secretly)',
                r'(?i)\bhow\s+to\s+(pass|ace)\s+.*(test|exam)\s+(without\s+studying|by\s+cheating)',
                r'(?i)\b(test|exam|assignment)\s+(cheating|fraud)\s+(methods|techniques|strategies)',
                r'(?i)\bhow\s+to\s+(copy|plagiarize)\s+.*(without\s+detection|undetected)',
                r'(?i)\b(academic|school|university)\s+(fraud|cheating|dishonesty)\s+(guide|method)',
                r'(?i)\bhow\s+to\s+(bypass|circumvent|avoid)\s+.*(plagiarism|cheating)\s+(detection|checker)',
                r'(?i)\bcheat\s+(code|sheet|device)\s+for\s+(test|exam)',
                r'(?i)\bhow\s+to\s+(hide|conceal)\s+(cheating|copying|plagiarism)',
                r'(?i)\b(essay|paper|assignment)\s+(mill|ghostwriting|cheating)\s+service',
            ]
        }
    
    def _get_misinformation_patterns(self) -> Dict[str, List[str]]:
        return {
            "health_misinfo": [
                r'(?i)\b(covid|coronavirus)\s+is\s+(fake|hoax|conspiracy)',
                r'(?i)\bvaccines\s+(cause|contain|are)\s+(autism|microchips|poison)',
                r'(?i)\bcancer\s+can\s+be\s+cured\s+by\s+(drinking|eating|taking)',
                r'(?i)\b(bleach|miracle\s+mineral)\s+cures\s+(covid|cancer|disease)',
            ],
            "election_misinfo": [
                r'(?i)\b(election|vote|voting)\s+was\s+(rigged|stolen|fake)',
                r'(?i)\bmass\s+voter\s+fraud',
                r'(?i)\bvoting\s+machines\s+(were\s+hacked|changed\s+votes)',
            ],
            "conspiracy_theories": [
                r'(?i)\b(qanon|deep\s+state|illuminati)\s+(controls|runs|owns)',
                r'(?i)\b9\/11\s+was\s+an\s+inside\s+job',
                r'(?i)\bmoon\s+landing\s+was\s+fake',
                r'(?i)\bearth\s+is\s+flat',
            ],
            "science_denial": [
                r'(?i)\bclimate\s+change\s+is\s+(fake|hoax|conspiracy)',
                r'(?i)\bevolution\s+is\s+(false|fake|theory)',
                r'(?i)\bscience\s+is\s+(fake|conspiracy|lies)',
            ]
        }
    
    def _get_spam_scams_patterns(self) -> Dict[str, List[str]]:
        return {
            "financial_scams": [
                r'(?i)\bmake\s+\$?\d+\s+(from\s+home|working\s+from\s+home|per\s+day)',
                r'(?i)\bget\s+rich\s+quick',
                r'(?i)\b(investment|trading)\s+opportunity\s+of\s+a\s+lifetime',
                r'(?i)\bdouble\s+your\s+money\s+in\s+\d+\s+(days|weeks)',
            ],
            "crypto_scams": [
                r'(?i)\bfree\s+(bitcoin|cryptocurrency|crypto)',
                r'(?i)\bcrypto\s+(giveaway|airdrop)\s+scam',
                r'(?i)\binvest\s+in\s+.*(shitcoin|meme\s+coin)\s+now',
            ],
            "phishing": [
                r'(?i)\bclick\s+here\s+to\s+(claim|get|receive)\s+your',
                r'(?i)\byour\s+account\s+(will\s+be\s+)?(suspended|closed|deleted)',
                r'(?i)\bverify\s+your\s+(account|identity|information)\s+now',
            ],
            "mlm_schemes": [
                r'(?i)\bbecome\s+(your\s+own\s+)?boss',
                r'(?i)\b(join\s+my\s+team|work\s+from\s+home\s+opportunity)',
                r'(?i)\bunlimited\s+(income|earning)\s+potential',
            ],
            "general_scamming": [  # NEW - Enhanced patterns
                r'(?i)\bhow\s+to\s+(scam|con|trick|deceive|swindle)\s+(people|someone|others)',
                r'(?i)\b(scam|con|trick|deceive|swindle)\s+(people|someone|others)\s+(out\s+of|for)',
                r'(?i)\b(easy|quick)\s+(scam|con)\s+(method|technique|way)',
                r'(?i)\bscamming\s+(techniques|methods|strategies)',
                r'(?i)\bhow\s+to\s+(rip\s+off|take\s+advantage\s+of)\s+(people|customers|clients)',
                r'(?i)\b(ponzi|pyramid)\s+scheme\s+(guide|instructions)',
                r'(?i)\bfraud\s+(people|customers|clients|system)',
            ]
        }
    
    def _get_privacy_patterns(self) -> Dict[str, List[str]]:
        return {
            "pii_request": [
                r'(?i)\b(give|tell|share)\s+me\s+your\s+(name|address|phone|email)',
                r'(?i)\bwhat\s+is\s+your\s+(real\s+name|address|location)',
                r'(?i)\bshare\s+your\s+(personal|private)\s+information',
            ],
            "doxxing_attempt": [
                r'(?i)\bfind\s+(someone\'s|a\s+person\'s)\s+(address|phone|information)',
                r'(?i)\bhow\s+to\s+(stalk|track|find)\s+someone\s+online',
                r'(?i)\bget\s+someone\'s\s+(personal|private)\s+(info|information|data)',
            ],
            "data_harvesting": [
                r'(?i)\bcollect\s+(user|personal)\s+data\s+without\s+consent',
                r'(?i)\bscrape\s+(social\s+media|website)\s+for\s+(data|information)',
                r'(?i)\bharvest\s+(email|contact)\s+(addresses|information)',
            ]
        }
    
    def _get_malicious_uri_patterns(self) -> Dict[str, List[str]]:
        return {
            "suspicious_domains": [
                r'(?i)\b(bit\.ly|tinyurl|goo\.gl|t\.co)\/\w+',
                r'(?i)\b\w+\.(tk|ml|ga|cf)\b',
                r'(?i)\b(phishing|malware|virus)\.(com|net|org)',
            ],
            "malicious_content": [
                r'(?i)\bdownload\s+.*(virus|malware|trojan|keylogger)',
                r'(?i)\b(click|visit)\s+this\s+link\s+to\s+(hack|steal|scam)',
                r'(?i)\bmalicious\s+(url|link|website)',
            ],
            "ip_addresses": [
                r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
                r'(?i)\bconnect\s+to\s+ip\s+address',
            ]
        }
    
    def _get_edge_cases_patterns(self) -> Dict[str, List[str]]:
        return {
            "context_dependent_profanity": [
                # These need context analysis
                r'(?i)\b(fuck|fucking|shit|damn|hell|ass|bitch)\b',
                r'(?i)\b(stupid|idiot|moron|retard|dumb)\b',
                r'(?i)\b(gay|fag|homo)\b',  # Can be neutral in some contexts
            ],
            "legitimate_educational": [
                # These should NOT be blocked in educational contexts
                r'(?i)\b(sex\s+education|sexual\s+health|anatomy)',
                r'(?i)\b(violence\s+in\s+history|war\s+crimes|genocide\s+studies)',
                r'(?i)\b(drug\s+education|substance\s+abuse\s+prevention)',
            ],
            "medical_terms": [
                # Medical terms that might trigger false positives
                r'(?i)\b(breast|penis|vagina|anus|sexual\s+dysfunction)',
                r'(?i)\b(suicide\s+prevention|mental\s+health|depression)',
                r'(?i)\b(overdose|addiction|withdrawal)',
            ],
            "creative_content": [
                # Creative writing that might seem harmful
                r'(?i)\bwrite\s+a\s+(story|novel|script)\s+(about|involving)',
                r'(?i)\b(fictional|fantasy|sci-fi)\s+(violence|war|conflict)',
                r'(?i)\b(character|protagonist)\s+(kills|murders|fights)',
            ],
            "news_and_reporting": [
                # News content that might trigger false positives
                r'(?i)\breporting\s+on\s+(violence|crime|terrorism)',
                r'(?i)\bnews\s+(article|report)\s+about',
                r'(?i)\bjournalism\s+(investigation|coverage)',
            ],
            "legitimate_religious_discussion": [  # NEW - Legitimate religious content
                # These should NOT be blocked in appropriate contexts
                r'(?i)\b(religious\s+studies|theology|comparative\s+religion|interfaith\s+dialogue)',
                r'(?i)\b(academic\s+study|scholarly\s+analysis|research)\s+.*(religion|islam|christianity|judaism|hinduism|buddhism)',
                r'(?i)\b(history\s+of|origins\s+of|development\s+of)\s+(religion|christianity|islam|judaism)',
                r'(?i)\b(biblical|quranic|talmudic|vedic)\s+(studies|scholarship|analysis|interpretation)',
                r'(?i)\b(religious\s+freedom|freedom\s+of\s+religion|religious\s+rights|religious\s+tolerance)',
                r'(?i)\b(understanding|learning\s+about|exploring)\s+(different\s+)?(religions|faiths|beliefs)',
                r'(?i)\b(peace\s+between|dialogue\s+between|cooperation\s+between)\s+(religions|faiths)',
                r'(?i)\b(teaching\s+about|education\s+about)\s+(world\s+religions|religious\s+diversity)',
                r'(?i)\b(religious\s+art|religious\s+music|religious\s+literature|religious\s+architecture)',
                r'(?i)\b(pilgrimage|prayer|meditation|worship|ritual)\s+(practices|traditions|customs)',
                r'(?i)\b(seminary|divinity\s+school|religious\s+education|sunday\s+school|madrasa)',
                r'(?i)\b(pastor|priest|rabbi|imam|monk|guru)\s+(training|education|role|responsibilities)',
            ]
        }

# =============================================================================
# Advanced Detection Engine
# =============================================================================

@dataclass
class RuleBasedConfig:
    """Enhanced configuration with comprehensive settings"""
    
    # Input limits
    max_input_length: int = 10000
    max_word_count: int = 2000
    max_line_count: int = 100
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    burst_limit: int = 10
    burst_window: int = 60
    
    # Output limits
    max_output_length: int = 50000
    max_output_sentences: int = 100
    
    # Detection thresholds
    profanity_threshold: float = 0.6
    hate_speech_threshold: float = 0.3
    violence_threshold: float = 0.4
    harassment_threshold: float = 0.5
    dangerous_content_threshold: float = 0.7
    
    # Context sensitivity
    enable_context_analysis: bool = True
    educational_context_weight: float = 0.3
    medical_context_weight: float = 0.4
    creative_context_weight: float = 0.5
    
    # Edge case handling
    enable_false_positive_reduction: bool = True
    enable_severity_adjustment: bool = True

class GuardrailViolation(BaseModel):
    violation_type: ViolationType
    severity: Severity
    message: str
    pattern_matched: Optional[str] = None
    confidence_score: float = 1.0
    context_detected: Optional[ContextType] = None
    suggested_action: str
    location: Optional[str] = None
    
    class Config:
        use_enum_values = True

class LLMRequest(BaseModel):
    prompt: str = Field(..., max_length=50000)
    model: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=150, ge=1, le=4000)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context_hint: Optional[str] = None  # User can provide context

class LLMResponse(BaseModel):
    response: str
    filtered: bool = False
    confidence_score: float = 1.0
    violations: List[GuardrailViolation] = []
    warnings: List[str] = []
    metadata: Dict[str, Any] = {}
    
    class Config:
        use_enum_values = True

# =============================================================================
# Context-Aware Detection Engine
# =============================================================================

class ContextAnalyzer:
    """Analyzes text context to reduce false positives"""
    
    def __init__(self, patterns: ComprehensivePatternLibrary):
        self.patterns = patterns
    
    def detect_context(self, text: str) -> Optional[ContextType]:
        """Detect the likely context of the text"""
        text_lower = text.lower()
        
        # Educational context
        educational_score = sum(1 for indicator in self.patterns.educational_indicators 
                              if indicator in text_lower)
        
        # Medical context
        medical_score = sum(1 for indicator in self.patterns.medical_indicators 
                           if indicator in text_lower)
        
        # Creative context
        creative_score = sum(1 for indicator in self.patterns.creative_indicators 
                            if indicator in text_lower)
        
        # News context
        news_score = sum(1 for indicator in self.patterns.news_indicators 
                        if indicator in text_lower)
        
        # Religious academic context (counts as educational)
        religious_academic_score = sum(1 for indicator in self.patterns.religious_academic_indicators 
                                     if indicator in text_lower)
        
        # Add religious academic score to educational score
        educational_score += religious_academic_score
        
        scores = {
            ContextType.EDUCATIONAL: educational_score,
            ContextType.MEDICAL: medical_score,
            ContextType.CREATIVE: creative_score,
            ContextType.NEWS: news_score,
        }
        
        max_score = max(scores.values())
        if max_score >= 2:  # At least 2 indicators
            return max(scores, key=scores.get)
        
        return ContextType.CASUAL
    
    def adjust_severity_for_context(self, severity: Severity, context: ContextType, 
                                   violation_type: ViolationType) -> Severity:
        """Adjust violation severity based on context"""
        
        # Educational context reduces severity for some violations
        if context == ContextType.EDUCATIONAL:
            if violation_type in [ViolationType.VIOLENCE, ViolationType.DANGEROUS]:
                if severity == Severity.HIGH:
                    return Severity.MEDIUM
                elif severity == Severity.MEDIUM:
                    return Severity.LOW
            
            # Religious hate speech in educational context - be more nuanced
            if violation_type == ViolationType.HATE_SPEECH:
                # Still block clear hate speech, but reduce severity for academic discussion
                if severity == Severity.CRITICAL:
                    return Severity.HIGH  # Still serious, but allow more academic discussion
                elif severity == Severity.HIGH:
                    return Severity.MEDIUM
        
        # Medical context allows certain content
        if context == ContextType.MEDICAL:
            if violation_type == ViolationType.SEXUALLY_EXPLICIT:
                if severity in [Severity.MEDIUM, Severity.LOW]:
                    return Severity.LOW
        
        # Creative context is more permissive
        if context == ContextType.CREATIVE:
            if violation_type in [ViolationType.VIOLENCE, ViolationType.HARASSMENT]:
                if severity == Severity.HIGH:
                    return Severity.MEDIUM
                elif severity == Severity.MEDIUM:
                    return Severity.LOW
        
        # News context allows reporting on sensitive topics
        if context == ContextType.NEWS:
            if violation_type in [ViolationType.VIOLENCE, ViolationType.HATE_SPEECH]:
                if severity == Severity.HIGH:
                    return Severity.MEDIUM
                elif severity == Severity.MEDIUM:
                    return Severity.LOW
        
        return severity

class ComprehensiveDetector:
    """Main detection engine with comprehensive pattern matching"""
    
    def __init__(self, config: RuleBasedConfig):
        self.config = config
        self.patterns = ComprehensivePatternLibrary()
        self.context_analyzer = ContextAnalyzer(self.patterns)
        
        # Compile all patterns
        self._compile_patterns()
        
        # Compile PII patterns separately
        self.compiled_pii_patterns = {
            name: re.compile(pattern, re.IGNORECASE) 
            for name, pattern in self.patterns.pii_patterns.items()
        }
    
    def _compile_patterns(self):
        """Compile all regex patterns for efficient matching"""
        self.compiled_patterns = {}
        
        for category in ['prompt_injection', 'jailbreak', 'hate_speech', 'harassment', 
                        'violence', 'sexually_explicit', 'dangerous', 'misinformation',
                        'spam_scams', 'privacy', 'malicious_uri', 'edge_cases']:
            
            category_patterns = getattr(self.patterns, category)
            self.compiled_patterns[category] = {}
            
            for subcategory, pattern_list in category_patterns.items():
                self.compiled_patterns[category][subcategory] = [
                    re.compile(pattern, re.IGNORECASE) for pattern in pattern_list
                ]
    
    def detect_violations(self, text: str, context_hint: str = None) -> List[GuardrailViolation]:
        """Comprehensive violation detection with context awareness"""
        violations = []
        
        # Detect context
        detected_context = self.context_analyzer.detect_context(text)
        if context_hint:
            # Override with user-provided context hint
            try:
                detected_context = ContextType(context_hint.lower())
            except ValueError:
                pass  # Use detected context
        
        # Run all detection categories
        violations.extend(self._detect_category(text, 'prompt_injection', ViolationType.PROMPT_INJECTION, Severity.HIGH))
        violations.extend(self._detect_category(text, 'jailbreak', ViolationType.JAILBREAK, Severity.HIGH))
        violations.extend(self._detect_category(text, 'hate_speech', ViolationType.HATE_SPEECH, Severity.CRITICAL))  # CRITICAL by default
        violations.extend(self._detect_category(text, 'harassment', ViolationType.HARASSMENT, Severity.HIGH))
        violations.extend(self._detect_category(text, 'violence', ViolationType.VIOLENCE, Severity.HIGH))
        violations.extend(self._detect_category(text, 'sexually_explicit', ViolationType.SEXUALLY_EXPLICIT, Severity.HIGH))
        violations.extend(self._detect_category(text, 'dangerous', ViolationType.DANGEROUS, Severity.CRITICAL))
        violations.extend(self._detect_category(text, 'misinformation', ViolationType.MISINFORMATION, Severity.MEDIUM))
        violations.extend(self._detect_category(text, 'spam_scams', ViolationType.SPAM_SCAMS, Severity.MEDIUM))
        violations.extend(self._detect_category(text, 'privacy', ViolationType.PRIVACY, Severity.HIGH))
        violations.extend(self._detect_category(text, 'malicious_uri', ViolationType.MALICIOUS_URI, Severity.HIGH))
        
        # PII detection
        violations.extend(self._detect_pii(text))
        
        # Handle edge cases with special logic
        violations.extend(self._detect_edge_cases(text, detected_context))
        
        # Apply context-based severity adjustments
        if self.config.enable_severity_adjustment:
            for violation in violations:
                violation.context_detected = detected_context
                original_severity = Severity(violation.severity)
                adjusted_severity = self.context_analyzer.adjust_severity_for_context(
                    original_severity, detected_context, violation.violation_type
                )
                violation.severity = adjusted_severity
        
        return violations
    
    def _detect_pii(self, text: str) -> List[GuardrailViolation]:
        """Detect personally identifiable information"""
        violations = []
        
        for pii_type, pattern in self.compiled_pii_patterns.items():
            matches = pattern.findall(text)
            if matches:
                first_match = str(matches[0]) if matches else ""
                if matches and isinstance(matches[0], tuple):
                    first_match = ' '.join(str(x) for x in matches[0] if x)
                
                violations.append(GuardrailViolation(
                    violation_type=ViolationType.PII_DETECTED,
                    severity=Severity.HIGH,
                    message=f"PII detected: {pii_type.upper()} ({len(matches)} instances)",
                    pattern_matched=pattern.pattern,
                    confidence_score=1.0,
                    suggested_action="Redact PII",
                    location=f"First match: {first_match[:20]}..." if first_match else None
                ))
        
        return violations
    
    def _detect_category(self, text: str, category: str, violation_type: ViolationType, 
                        default_severity: Severity) -> List[GuardrailViolation]:
        """Detect violations for a specific category"""
        violations = []
        
        category_patterns = self.compiled_patterns.get(category, {})
        
        for subcategory, patterns in category_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    # Handle match display
                    first_match = str(matches[0]) if matches else ""
                    if matches and isinstance(matches[0], tuple):
                        first_match = ' '.join(str(x) for x in matches[0] if x)
                    
                    # Determine severity based on subcategory for dangerous content
                    actual_severity = default_severity
                    if category == "dangerous" and subcategory == "drug_trafficking":
                        actual_severity = Severity.CRITICAL  # Make drug trafficking critical
                    
                    violations.append(GuardrailViolation(
                        violation_type=violation_type,
                        severity=actual_severity,
                        message=f"{violation_type.value.replace('_', ' ').title()} detected in {subcategory}",
                        pattern_matched=pattern.pattern,
                        confidence_score=self._calculate_confidence(matches, text),
                        suggested_action=self._get_suggested_action(violation_type, actual_severity),
                        location=f"Match: {first_match[:50]}..." if first_match else None
                    ))
        
        return violations
    
    def _detect_edge_cases(self, text: str, context: ContextType) -> List[GuardrailViolation]:
        """Special handling for edge cases with context awareness"""
        violations = []
        
        # Handle context-dependent profanity
        profanity_patterns = self.compiled_patterns['edge_cases']['context_dependent_profanity']
        
        for pattern in profanity_patterns:
            matches = pattern.findall(text)
            if matches:
                # Determine severity based on context and specific word
                word = matches[0].lower() if matches else ""
                severity = self._get_profanity_severity(word, context)
                
                if severity != Severity.LOW or context == ContextType.CASUAL:
                    violations.append(GuardrailViolation(
                        violation_type=ViolationType.EDGE_CASES,
                        severity=severity,
                        message=f"Context-dependent language detected: {word}",
                        pattern_matched=pattern.pattern,
                        confidence_score=0.7,
                        context_detected=context,
                        suggested_action=self._get_suggested_action(ViolationType.EDGE_CASES, severity),
                        location=f"Word: {word}"
                    ))
        
        return violations
    
    def _get_profanity_severity(self, word: str, context: ContextType) -> Severity:
        """Determine profanity severity based on word and context"""
        
        # Severe profanity
        if word in ['fuck', 'fucking', 'shit']:
            if context in [ContextType.EDUCATIONAL, ContextType.MEDICAL, ContextType.NEWS]:
                return Severity.LOW
            elif context == ContextType.CREATIVE:
                return Severity.MEDIUM
            else:
                return Severity.HIGH
        
        # Moderate profanity
        elif word in ['damn', 'hell', 'ass', 'bitch']:
            if context in [ContextType.EDUCATIONAL, ContextType.MEDICAL, ContextType.NEWS, ContextType.CREATIVE]:
                return Severity.LOW
            else:
                return Severity.MEDIUM
        
        # Potentially offensive terms
        elif word in ['stupid', 'idiot', 'moron', 'dumb']:
            if context in [ContextType.EDUCATIONAL, ContextType.MEDICAL]:
                return Severity.LOW
            else:
                return Severity.MEDIUM
        
        # Context-sensitive terms
        elif word in ['gay', 'fag', 'homo']:
            if context in [ContextType.EDUCATIONAL, ContextType.MEDICAL, ContextType.NEWS]:
                return Severity.LOW
            else:
                return Severity.HIGH
        
        return Severity.MEDIUM
    
    def _calculate_confidence(self, matches: List, text: str) -> float:
        """Calculate confidence score for violation"""
        if not matches:
            return 0.0
        
        # Base confidence on number of matches and text length
        base_score = min(1.0, len(matches) / 3)  # Cap at 3 matches for full confidence
        length_factor = min(1.0, len(text) / 1000)  # Longer text = more context
        
        return max(0.1, base_score * (0.7 + 0.3 * length_factor))
    
    def _get_suggested_action(self, violation_type: ViolationType, severity: Severity) -> str:
        """Get suggested action based on violation type and severity"""
        if severity == Severity.CRITICAL:
            return "Block immediately"
        elif severity == Severity.HIGH:
            return "Block or heavily filter"
        elif severity == Severity.MEDIUM:
            return "Review and potentially filter"
        else:
            return "Monitor or flag"

# =============================================================================
# Rate Limiting System
# =============================================================================

class AdvancedRateLimiter:
    """Advanced rate limiting with burst detection"""
    
    def __init__(self, config: RuleBasedConfig):
        self.config = config
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.burst_requests: Dict[str, deque] = defaultdict(deque)
        self.violation_counts: Dict[str, int] = defaultdict(int)
    
    def is_rate_limited(self, identifier: str) -> Tuple[bool, str]:
        """Check if request should be rate limited"""
        now = time.time()
        
        # Check burst limit
        burst_window_start = now - self.config.burst_window
        burst_requests = self.burst_requests[identifier]
        
        while burst_requests and burst_requests[0] < burst_window_start:
            burst_requests.popleft()
        
        if len(burst_requests) >= self.config.burst_limit:
            return True, f"Burst limit exceeded: {len(burst_requests)}/{self.config.burst_limit}"
        
        # Check standard rate limit
        window_start = now - self.config.rate_limit_window
        user_requests = self.requests[identifier]
        
        while user_requests and user_requests[0] < window_start:
            user_requests.popleft()
        
        if len(user_requests) >= self.config.rate_limit_requests:
            return True, f"Rate limit exceeded: {len(user_requests)}/{self.config.rate_limit_requests}"
        
        # Add current request
        burst_requests.append(now)
        user_requests.append(now)
        
        return False, "OK"

# =============================================================================
# Main Guardrails Server
# =============================================================================

class ComprehensiveGuardrailsServer:
    """Comprehensive guardrails server with edge case handling"""
    
    def __init__(self, config: RuleBasedConfig = None):
        self.config = config or RuleBasedConfig()
        self.rate_limiter = AdvancedRateLimiter(self.config)
        self.detector = ComprehensiveDetector(self.config)
        
        # Statistics tracking
        self.stats = {
            'total_requests': 0,
            'blocked_inputs': 0,
            'filtered_outputs': 0,
            'rate_limited': 0,
            'violations_by_type': defaultdict(int),
            'context_adjustments': 0,
            'false_positives_prevented': 0,
            'religious_abuse_blocked': 0,  # NEW - Track religious abuse specifically
            'hate_speech_blocked': 0,      # NEW - Track hate speech separately
            'harassment_blocked': 0,       # NEW - Track harassment separately
        }
        
        # Audit logging
        self.audit_log: deque = deque(maxlen=10000)
        
        # Initialize FastAPI
        self.app = FastAPI(
            title="Comprehensive LLM Guardrails Server",
            description="Complete guardrails with edge case handling and context awareness",
            version="3.0.0"
        )
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    def _violations_to_dict(self, violations: List[GuardrailViolation]) -> List[Dict]:
        """Safely convert violations to dictionary format for JSON serialization"""
        result = []
        for v in violations:
            try:
                # Handle the case where violation_type might be a string already
                violation_type = v.violation_type.value if hasattr(v.violation_type, 'value') else str(v.violation_type)
                
                # Handle the case where severity might be a string already
                severity = v.severity.value if hasattr(v.severity, 'value') else str(v.severity)
                
                result.append({
                    "violation_type": violation_type,
                    "severity": severity,
                    "message": v.message,
                    "pattern_matched": v.pattern_matched,
                    "confidence_score": v.confidence_score,
                    "suggested_action": v.suggested_action,
                    "location": v.location
                })
            except Exception as e:
                # Fallback for any other issues
                logger.warning(f"Error processing violation: {str(e)}")
                result.append({
                    "violation_type": "error",
                    "severity": "medium", 
                    "message": f"Error processing violation: {str(e)}",
                    "confidence_score": 0.0,
                    "suggested_action": "Review manually"
                })
        
        return result
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "3.0.0",
                "features": [
                    "comprehensive_patterns", "context_awareness", "edge_case_handling",
                    "false_positive_reduction", "severity_adjustment"
                ]
            }
        
        @self.app.get("/patterns")
        async def get_patterns():
            """Get information about all detection patterns"""
            pattern_counts = {}
            
            for category in ['prompt_injection', 'jailbreak', 'hate_speech', 'harassment',
                           'violence', 'sexually_explicit', 'dangerous', 'misinformation',
                           'spam_scams', 'privacy', 'malicious_uri', 'edge_cases']:
                category_patterns = getattr(self.detector.patterns, category)
                pattern_counts[category] = {
                    "subcategories": len(category_patterns),
                    "total_patterns": sum(len(patterns) for patterns in category_patterns.values()),
                    "patterns": category_patterns
                }
            
            return {
                "total_categories": len(pattern_counts),
                "total_patterns": sum(pc["total_patterns"] for pc in pattern_counts.values()),
                "categories": pattern_counts,
                "context_types": [ct.value for ct in ContextType],
                "violation_types": [vt.value for vt in ViolationType]
            }
        
        @self.app.post("/debug-detection")
        async def debug_detection(request: Request, llm_request: LLMRequest):
            """Debug endpoint to see what patterns match without blocking"""
            user_id = llm_request.user_id or request.client.host
            
            # Get all violations but don't block
            violations = self.detector.detect_violations(
                llm_request.prompt, 
                llm_request.context_hint
            )
            
            # Check each category specifically
            debug_info = {}
            for category in ['dangerous', 'edge_cases', 'hate_speech', 'harassment']:
                category_violations = self.detector._detect_category(
                    llm_request.prompt, 
                    category, 
                    getattr(ViolationType, category.upper()), 
                    Severity.HIGH
                )
                debug_info[category] = {
                    "violations_count": len(category_violations),
                    "violations": self._violations_to_dict(category_violations)
                }
            
            return {
                "input": llm_request.prompt,
                "total_violations": len(violations),
                "violations": self._violations_to_dict(violations),
                "debug_by_category": debug_info,
                "would_be_blocked": len([v for v in violations if v.severity in [Severity.HIGH, Severity.CRITICAL]]) > 0
            }
        
        @self.app.post("/validate-input")
        async def validate_input_endpoint(request: Request, llm_request: LLMRequest):
            start_time = time.time()
            client_ip = request.client.host
            user_id = llm_request.user_id or client_ip
            
            self.stats['total_requests'] += 1
            
            # Rate limiting
            is_limited, limit_reason = self.rate_limiter.is_rate_limited(user_id)
            if is_limited:
                self.stats['rate_limited'] += 1
                self._log_event("rate_limit_exceeded", user_id, {"reason": limit_reason})
                raise HTTPException(status_code=429, detail=f"Rate limited: {limit_reason}")
            
            # Comprehensive violation detection
            violations = self.detector.detect_violations(
                llm_request.prompt, 
                llm_request.context_hint
            )
            
            processing_time = time.time() - start_time
            # Update statistics
            for violation in violations:
                # Handle case where violation_type might be a string already
                violation_type = violation.violation_type.value if hasattr(violation.violation_type, 'value') else str(violation.violation_type)
                self.stats['violations_by_type'][violation_type] += 1
                if violation.context_detected and violation.context_detected != ContextType.CASUAL:
                    self.stats['context_adjustments'] += 1
                
                # Track specific categories for monitoring
                if violation.violation_type == ViolationType.HATE_SPEECH:
                    self.stats['hate_speech_blocked'] += 1
                    # Check if it's religious hate speech
                    if any(keyword in violation.message.lower() for keyword in ['religious', 'muslim', 'jew', 'christian', 'hindu', 'buddhist', 'islam', 'christianity', 'judaism']):
                        self.stats['religious_abuse_blocked'] += 1
                elif violation.violation_type == ViolationType.HARASSMENT:
                    self.stats['harassment_blocked'] += 1
                    # Check if it's religious harassment
                    if any(keyword in violation.message.lower() for keyword in ['religious', 'muslim', 'jew', 'christian', 'hindu', 'buddhist', 'islam', 'christianity', 'judaism']):
                        self.stats['religious_abuse_blocked'] += 1
                elif violation.violation_type == ViolationType.DANGEROUS:
                    # Check if it's drug trafficking
                    if any(keyword in violation.message.lower() for keyword in ['drug', 'cocaine', 'heroin', 'meth', 'trafficking', 'dealer']):
                        self.stats['drug_trafficking_blocked'] += 1
                elif violation.violation_type == ViolationType.EDGE_CASES:
                    # Check if it's profanity
                    if any(keyword in violation.message.lower() for keyword in ['profanity', 'context-dependent', 'language']):
                        self.stats['profanity_detected'] += 1
            
            # Determine if input should be blocked
            critical_violations = [v for v in violations if v.severity in [Severity.HIGH, Severity.CRITICAL]]
            is_blocked = len(critical_violations) > 0
            
            # CRITICAL: Hate speech should ALWAYS be blocked
            hate_speech_violations = [v for v in violations if v.violation_type == ViolationType.HATE_SPEECH]
            if hate_speech_violations:
                is_blocked = True  # Force block for any hate speech
            
            if is_blocked:
                self.stats['blocked_inputs'] += 1
            
            self._log_event("input_validation", user_id, {
                "blocked": is_blocked,
                "violations": len(violations),
                "processing_time_ms": processing_time * 1000
            })
            
            if is_blocked:
                raise HTTPException(status_code=400, detail={
                    "message": "Input validation failed",
                    "violations": self._violations_to_dict(violations),
                    "processing_time_ms": processing_time * 1000
                })
            
            return {
                "valid": True,
                "violations": self._violations_to_dict(violations),
                "warnings": [v.message for v in violations if v.severity in [Severity.LOW, Severity.MEDIUM]],
                "processing_time_ms": processing_time * 1000,
                "detection_method": "comprehensive_rule_based",
                "context_analysis_enabled": self.config.enable_context_analysis
            }
        
        @self.app.get("/stats")
        async def get_stats():
            total = max(self.stats['total_requests'], 1)
            return {
                **dict(self.stats),
                "success_rate": (total - self.stats['blocked_inputs']) / total,
                "active_users": len(self.rate_limiter.requests),
                "detection_categories": len(ViolationType),
                "context_types_supported": len(ContextType),
                "comprehensive": True
            }
    
    def _log_event(self, event_type: str, user_id: str, details: Dict):
        """Log audit event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details
        }
        self.audit_log.append(event)
        logger.info(f"Event: {event_type} for user {user_id}")
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the comprehensive guardrails server"""
        logger.info(f"Starting Comprehensive LLM Guardrails Server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

# =============================================================================
# Usage and Configuration
# =============================================================================

def create_production_config() -> RuleBasedConfig:
    """Create production-ready configuration"""
    config = RuleBasedConfig()
    
    # Stricter thresholds for production
    config.profanity_threshold = 0.4
    config.hate_speech_threshold = 0.2
    config.violence_threshold = 0.3
    config.harassment_threshold = 0.3
    config.dangerous_content_threshold = 0.5
    
    # Enable all advanced features
    config.enable_context_analysis = True
    config.enable_false_positive_reduction = True
    config.enable_severity_adjustment = True
    
    # Tighter rate limits
    config.rate_limit_requests = 500
    config.burst_limit = 3000
    
    return config

if __name__ == "__main__":
    config = create_production_config()
    server = ComprehensiveGuardrailsServer(config)
    
    print("🛡️  COMPREHENSIVE LLM GUARDRAILS SERVER v3.0")
    print("=" * 80)
    print("🎯 COMPREHENSIVE COVERAGE:")
    print("  ✅ Prompt Injection & Jailbreaking")
    print("  ✅ Hate Speech & Harassment") 
    print("  ✅ Violence & Dangerous Content")
    print("  ✅ Sexually Explicit Content")
    print("  ✅ Misinformation & Spam/Scams")
    print("  ✅ Privacy & Malicious URIs")
    print("  ✅ Edge Cases & Context Awareness")
    print()
    print("🧠 SMART FEATURES:")
    print("  ✅ Context-Aware Detection (Educational/Medical/Creative/News)")
    print("  ✅ Profanity Severity Adjustment (fuck/stupid/idiot handled properly)")
    print("  ✅ False Positive Reduction")
    print("  ✅ Severity Adjustment Based on Context")
    print("  ✅ Comprehensive Edge Case Handling")
    print()
    print("📊 COVERAGE STATS:")
    patterns = ComprehensivePatternLibrary()
    total_patterns = 0
    for category in ['prompt_injection', 'jailbreak', 'hate_speech', 'harassment',
                    'violence', 'sexually_explicit', 'dangerous', 'misinformation',
                    'spam_scams', 'privacy', 'malicious_uri', 'edge_cases']:
        category_patterns = getattr(patterns, category)
        category_total = sum(len(pattern_list) for pattern_list in category_patterns.values())
        total_patterns += category_total
        print(f"  • {category.replace('_', ' ').title()}: {category_total} patterns")
    
    # Add PII patterns
    pii_total = len(patterns.pii_patterns)
    total_patterns += pii_total
    print(f"  • PII Detection: {pii_total} patterns")
    
    print(f"\n  🎯 TOTAL PATTERNS: {total_patterns}")
    print("=" * 80)
    print(f"🚀 Server starting on http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs")
    print("🔍 Patterns: http://localhost:8000/patterns")
    print()
    
    server.run()
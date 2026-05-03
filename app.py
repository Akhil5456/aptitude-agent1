import streamlit as st
import random, time, json, os, requests

st.set_page_config(page_title="AI Aptitude Agent")

# ----------- INIT SESSION STATE FIRST ----------- #
if "login" not in st.session_state:
    st.session_state.login = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# Debug info
st.sidebar.write(f"Debug: login={st.session_state.login}, user={st.session_state.user}, page={st.session_state.page}")
st.sidebar.write(f"Debug: cur={st.session_state.get('cur', 'N/A')}, quiz_len={len(st.session_state.get('quiz', []))}")

# ----------- CLEAN UI ----------- #
st.markdown("""
<style>
html, body, .stApp {
    background-color: #f0e6ff !important;
    color: black !important;
}
label, p, h1, h2, h3, h4, h5, h6, span, div {
    color: black !important;
}
input, textarea {
    background-color: white !important;
    color: black !important;
    border: 1px solid #ccc !important;
}
button {
    background-color: #4CAF50 !important;
    color: white !important;
}
/* Prevent code highlighting in radio options */
st-emotion-cache-1c7y6kd code, .stRadio code, .stRadio pre {
    background-color: transparent !important;
    color: black !important;
    font-family: inherit !important;
    padding: 0 !important;
}
.stRadio span {
    color: black !important;
}
/* Fix multiselect dropdown - target all possible elements */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="popover"] > div > div,
[data-baseweb="menu"],
[data-baseweb="menu"] > div,
[data-baseweb="menu"] > div > div,
[role="listbox"],
[role="option"],
.stMultiSelect [class*="menu"],
.stMultiSelect [class*="option"] {
    background-color: white !important;
    color: black !important;
}
[role="option"]:hover,
[aria-selected="true"] {
    background-color: #e6e6fa !important;
}
/* Force all descendants */
[data-baseweb="popover"] * {
    background-color: white !important;
}
/* Target the dropdown overlay specifically */
[class*="stMultiSelect"] div[class*="menu"] {
    background: white !important;
}
/* Fix results page code highlighting */
.stWrite code, .stWrite pre, [data-testid="stMarkdown"] code, [data-testid="stMarkdown"] pre {
    background-color: transparent !important;
    color: black !important;
    font-family: inherit !important;
    padding: 0 !important;
    border: none !important;
}
/* Fix main container background */
[data-testid="stAppViewContainer"] {
    background-color: #f0e6ff !important;
}
/* Fix multiselect input area */
.stMultiSelect div[role="button"] {
    background-color: white !important;
}
.stMultiSelect input {
    background-color: white !important;
    color: black !important;
}
/* Target the specific multiselect container */
[data-testid="stMultiSelect"] > div > div {
    background-color: white !important;
}
[data-testid="stMultiSelect"] [data-baseweb="select"] {
    background-color: white !important;
}
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
    background-color: white !important;
}
</style>
<script>
// Force white background on multiselect
function fixMultiselect() {
    const elements = document.querySelectorAll('[data-baseweb="select"], [data-baseweb="popover"], [data-baseweb="menu"]');
    elements.forEach(el => {
        el.style.backgroundColor = 'white';
        el.style.setProperty('background-color', 'white', 'important');
    });
}
setInterval(fixMultiselect, 500);
</script>
""", unsafe_allow_html=True)

# ----------- API KEY ----------- #
API_KEY = "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"

def ask_gemini(q):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an aptitude expert. Answer clearly."
                },
                {
                    "role": "user",
                    "content": q
                }
            ]
        }

        r = requests.post(url, headers=headers, json=data)

        if r.status_code != 200:
            return f"API Error: {r.text}"

        res = r.json()

        return res["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {str(e)}"

def generate_ai_question(topic, level):
    """Generate exam-level AI questions with scenarios"""
    
    scenario_prompts = {
        "Percentage": [
            "A company's revenue analysis: A retail store had monthly sales of $X. In the first quarter, sales increased by Y%, then decreased by Z% in the second quarter. Calculate the final sales amount.",
            "Investment scenario: An investor puts $X in a stock that grows by Y% in year 1, loses Z% in year 2, then gains W% in year 3. What's the final value?",
            "Population growth: A city has X residents. The population grows by Y% annually due to migration and Z% due to births. Calculate the population after N years."
        ],
        "Ratio": [
            "Business partnership: Two partners invest in the ratio X:Y. If the total profit is $Z, how much does each partner get? Also consider that one partner worked 2x more hours.",
            "Recipe scaling: A recipe serves X people and requires ingredients in ratio A:B:C. How much of each ingredient is needed for Y people?",
            "Classroom distribution: In a school, the ratio of boys to girls is X:Y. If Z new students join, maintaining the same ratio, how many are boys and girls?"
        ],
        "Profit & Loss": [
            "Business operations: A manufacturer buys raw materials at $X per unit, spends $Y on labor per unit, and sells at $Z per unit. If they produce N units and have overhead costs of $M, what's the profit percentage?",
            "Retail scenario: A shopkeeper buys items at a wholesale price with X% discount. He adds Y% markup but offers Z% discount to customers. Calculate his effective profit percentage.",
            "Investment portfolio: An investor buys stocks at $X per share, sells at $Y per share, pays Z% brokerage fees. What's the net profit percentage?"
        ],
        "Time & Work": [
            "Project management: Team A can complete a project in X days, Team B in Y days. If they work together for Z days, then Team A leaves, how long will Team B take to finish?",
            "Factory production: Machine A produces X items per hour, Machine B produces Y items per hour. If they work together for Z hours, then Machine A breaks down, how many more hours does Machine B need?",
            "Construction scenario: X workers can build a house in Y days. After Z days, W workers leave. How many more days will the remaining workers take?"
        ],
        "Probability": [
            "Quality control: A factory produces items with X% defect rate. If Y items are tested, what's the probability of finding exactly Z defective items?",
            "Weather prediction: Based on historical data, the probability of rain on any day is X%. What's the probability of rain on exactly Y out of Z days?",
            "Medical testing: A disease affects X% of population. A test is Y% accurate for positive cases and Z% accurate for negative cases. What's the probability a person has the disease if they test positive?"
        ]
    }
    
    level_multipliers = {"Easy": 1, "Medium": 1.5, "Hard": 2}
    multiplier = level_multipliers.get(level, 1)
    
    scenarios = scenario_prompts.get(topic, ["Generate a " + topic + " problem"])
    scenario = random.choice(scenarios)
    
    prompt = f"""
    Generate a challenging {level} level {topic} question based on this scenario:
    {scenario}
    
    Requirements:
    1. Make it exam-level difficulty
    2. Include realistic numbers and context
    3. Make the question detailed and comprehensive
    4. Provide 4 multiple choice options (A, B, C, D)
    5. Clearly indicate the correct answer
    6. Format as JSON: {{"question": "...", "options": ["A", "B", "C", "D"], "answer": "A"}}
    """
    
    try:
        response = ask_gemini(prompt)
        
        # Try to extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            question_data = json.loads(json_match.group())
            return {
                "q": question_data.get("question", response),
                "a": question_data.get("answer", "A"),
                "o": question_data.get("options", ["A", "B", "C", "D"]),
                "t": topic,
                "type": "AI"
            }
        else:
            # Fallback if JSON parsing fails
            return {
                "q": response,
                "a": "A",
                "o": ["A", "B", "C", "D"],
                "t": topic,
                "type": "AI"
            }
    except:
        # Fallback to template question if AI fails
        return gen_q(topic, level)

# ----------- FILE SAFE ----------- #
FILE = "users.json"

def load():
    try:
        if os.path.exists(FILE):
            return json.load(open(FILE))
    except:
        return {}
    return {}

def save(d):
    with open(FILE, "w") as f:
        json.dump(d, f, indent=2)

users = load()

# ----------- LOGIN ----------- #
if not st.session_state.login:

    st.title("AI Aptitude Agent")

    mode = st.radio("Select", ["Login","Register","Forgot Password"])

    if mode == "Register":
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        f = st.text_input("Friend")
        s = st.text_input("School")
        pet = st.text_input("Pet")

        if st.button("Register"):
            users[u] = {"password":p,"sec":[f,s,pet],"perf":{},"count":0}
            save(users)
            st.success("Registered")

    elif mode == "Login":
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if u in users and users[u]["password"] == p:
                st.session_state.login = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        u = st.text_input("Username")
        if u in users:
            f = st.text_input("Friend")
            s = st.text_input("School")
            pet = st.text_input("Pet")
            np = st.text_input("New Password", type="password")

            if st.button("Reset"):
                if [f,s,pet] == users[u]["sec"]:
                    users[u]["password"] = np
                    save(users)
                    st.success("Password reset successful")

    st.stop()

# ----------- USER SAFE ----------- #
# Safely get user data - handle case where user might not be in users dict
if st.session_state.user and st.session_state.user in users:
    user = users[st.session_state.user]
else:
    user = {"perf": {}, "count": 0}
user.setdefault("perf", {})
user.setdefault("count", 0)

# ----------- COMPREHENSIVE TOPIC STRUCTURE ----------- #
APTITUDE_TOPICS = {
    "Numerical Aptitude": {
        "Number Systems": ["Decimal conversions", "Binary operations", "Prime factorization", "LCM HCF problems"],
        "Fractions and Decimals": ["Simplification", "Comparison", "Recurring decimals", "Operations"],
        "Percentages": ["Population growth", "Salary hike", "Discount problems", "Successive percentage"],
        "Ratios and Proportions": ["Partnership", "Alligation", "Mixtures", "Direct variation"],
        "Algebra": ["Linear equations", "Quadratic equations", "Age problems", "Work-rate formulas"],
        "Geometry": ["Area perimeter", "Volume surface", "Coordinate geometry", "Similar triangles"],
        "Trigonometry": ["Height distance", "Bearings", "Sin cos applications", "Navigation"],
        "Statistics": ["Mean median mode", "Standard deviation", "Weighted average", "Range problems"],
        "Data Interpretation": ["Pie charts", "Bar graphs", "Line charts", "Tabular data"]
    },
    "Verbal Aptitude": {
        "Vocabulary": ["Synonyms", "Antonyms", "Word meanings", "Contextual usage"],
        "Grammar": ["Tenses", "Clauses", "Sentence structure", "Parts of speech"],
        "Reading Comprehension": ["Passage analysis", "Inference", "Main idea", "Author's tone"],
        "Sentence Completion": ["Fill in blanks", "Context clues", "Logical connectors"],
        "Analogies": ["Word relationships", "Phrase analogies", "Classification"],
        "Logical Reasoning": ["Arguments", "Conclusions", "Assumptions", "Inference"],
        "Error Detection": ["Spotting errors", "Sentence correction", "Grammar errors"],
        "Para Jumbles": ["Sentence rearrangement", "Logical sequence", "Coherence"]
    },
    "Logical Reasoning": {
        "Deductive Reasoning": ["Syllogisms", "Logical deductions", "Venn diagrams"],
        "Inductive Reasoning": ["Pattern series", "Number series", "Letter series"],
        "Abductive Reasoning": ["Best explanation", "Hypothesis testing"],
        "Blood Relations": ["Family trees", "Coded relations", "Generation puzzles"],
        "Coding and Decoding": ["Letter coding", "Number coding", "Substitution", "Pattern coding"],
        "Directions and Distances": ["Route planning", "Shadow problems", "Navigation"],
        "Syllogisms": ["Statements conclusions", "Venn diagrams", "Logical arguments"],
        "Critical Reasoning": ["Strengthen weaken", "Assumption identification", "Inference"]
    },
    "Non-Verbal Aptitude": {
        "Visual Reasoning": ["Image patterns", "Mirror images", "Water images", "Paper folding"],
        "Spatial Reasoning": ["3D shapes", "Cube problems", "Dice", "Rotation"],
        "Pattern Recognition": ["Figure series", "Analogy patterns", "Missing figure"],
        "Abstract Reasoning": ["Shape relations", "Symbol logic", "Matrix patterns"],
        "Diagrammatic Reasoning": ["Flow charts", "Process diagrams", "Network diagrams"],
        "Non-Verbal Analogies": ["Figure analogies", "Pattern completion"],
        "Mirror Images": ["Horizontal mirrors", "Vertical mirrors", "Clock mirrors"],
        "Paper Folding and Cutting": ["Fold patterns", "Cut shapes", "Unfold prediction"]
    },
    "Data Analysis": {
        "Data Sufficiency": ["Quantity comparison", "Statement evaluation", "Two statements"],
        "Data Visualization": ["Chart interpretation", "Graph analysis", "Dashboard reading"],
        "Statistical Analysis": ["Probability", "Correlation", "Regression basics", "Distribution"],
        "Data Mining": ["Pattern identification", "Trend analysis", "Anomaly detection"],
        "Case Studies": ["Business scenarios", "Market analysis", "Financial cases"],
        "Business Scenario Analysis": ["Profit analysis", "Break-even", "ROI calculation"],
        "Graphical Analysis": ["Trend graphs", "Comparative charts", "Multi-axis graphs"],
        "Table Analysis": ["Data tables", "Comparative tables", "Multi-source tables"]
    }
}

# Flatten for selection
ALL_TOPICS = []
for main_cat, subtopics in APTITUDE_TOPICS.items():
    for subtopic in subtopics.keys():
        ALL_TOPICS.append(f"{main_cat} - {subtopic}")

# ----------- SESSION ----------- #
# Initialize session state with better persistence (page already initialized at top)
session_defaults = {
    "quiz": [],
    "ans": [],
    "cur": 0,
    "start": 0,
    "chat": [],
    "chat_input": "",
    "selected_categories": [],
    "user_difficulty_level": 1,  # 1-5 adaptive difficulty
    "consecutive_perfect_quizzes": 0,  # Track consecutive 100% scores at current level
    "total_quizzes_at_level": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}  # Track quizzes per level
}

for key, default_value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# Handle page refresh - preserve login state
if st.session_state.login and "user" in st.session_state:
    # Reload user data to ensure it's current
    users = load()
    user = users.get(st.session_state.user, {"perf": {}, "count": 0})
    user.setdefault("perf", {})
    user.setdefault("count", 0)

# ----------- QUESTION GENERATOR WITH ADAPTIVE DIFFICULTY ----------- #
def get_difficulty_params(user_level):
    """Get difficulty parameters based on user's adaptive level"""
    params = {
        1: {"complexity": "basic", "multi_step": False, "numbers": (10, 100)},
        2: {"complexity": "intermediate", "multi_step": False, "numbers": (50, 500)},
        3: {"complexity": "advanced", "multi_step": True, "numbers": (100, 1000)},
        4: {"complexity": "expert", "multi_step": True, "numbers": (500, 5000)},
        5: {"complexity": "master", "multi_step": True, "numbers": (1000, 10000)}
    }
    return params.get(min(user_level, 5), params[3])

def update_difficulty(correct, current_level):
    """Update difficulty based on user performance"""
    if correct:
        st.session_state.correct_streak += 1
        st.session_state.incorrect_streak = 0
        if st.session_state.correct_streak >= 2 and current_level < 5:
            return current_level + 1
    else:
        st.session_state.incorrect_streak += 1
        st.session_state.correct_streak = 0
        if st.session_state.incorrect_streak >= 2 and current_level > 1:
            return current_level - 1
    return current_level

def gen_ai_question(topic, level):
    """Generate AI-powered questions with level-based complexity for ALL topics"""
    
    # Define complexity based on level
    level_prompts = {
        1: "Generate a simple 1-2 line scenario question",
        2: "Generate a medium 2-3 line scenario question", 
        3: "Generate a moderate 3-4 line scenario question",
        4: "Generate a complex 4-5 line scenario question",
        5: "Generate a very complex 5-6 line scenario question"
    }
    
    # Define topic-specific requirements
    topic_requirements = {
        "Number Systems": "Focus on LCM, HCF, number properties, binary systems",
        "Fractions and Decimals": "Focus on operations, conversions, comparisons",
        "Percentages": "Focus on profit/loss, discounts, growth rates, calculations",
        "Ratios and Proportions": "Focus on partnerships, mixtures, scaling, distributions",
        "Algebra": "Focus on equations, word problems, age problems",
        "Geometry": "Focus on area, volume, perimeter, shapes, measurements",
        "Trigonometry": "Focus on heights, distances, angles, practical applications",
        "Statistics": "Focus on mean, median, mode, probability, data analysis",
        "Data Interpretation": "Focus on charts, graphs, tables, data reading",
        "Vocabulary": "Focus on synonyms, antonyms, word meanings",
        "Reading Comprehension": "Focus on passage analysis, inference, main ideas",
        "Grammar": "Focus on error detection, sentence correction, parts of speech",
        "Analogies": "Focus on relationships, patterns, logical connections",
        "Blood Relations": "Focus on family relationships, logical deduction",
        "Coding and Decoding": "Focus on letter/number codes, pattern recognition",
        "Directions and Distances": "Focus on spatial reasoning, navigation, calculations",
        "Syllogisms": "Focus on logical conclusions, deductive reasoning",
        "Deductive Reasoning": "Focus on logical inference, conclusion drawing",
        "Inductive Reasoning": "Focus on pattern completion, series, generalization",
        "Visual Reasoning": "Focus on shapes, patterns, spatial visualization",
        "Pattern Recognition": "Focus on sequences, arrangements, logical patterns",
        "Abstract Reasoning": "Focus on non-verbal logic, conceptual thinking",
        "Spatial Reasoning": "Focus on 3D visualization, rotations, transformations",
        "Paper Folding and Cutting": "Focus on mental visualization, pattern prediction",
        "Mirror Images": "Focus on reflection, symmetry, visual processing",
        "Data Sufficiency": "Focus on logical analysis, information adequacy",
        "Data Visualization": "Focus on chart interpretation, graphical analysis",
        "Graphical Analysis": "Focus on graph reading, trend analysis",
        "Table Analysis": "Focus on data tables, comparisons, calculations",
        "Statistical Analysis": "Focus on statistical measures, data interpretation",
        "Data Mining": "Focus on pattern recognition in data, insights",
        "Case Studies": "Focus on business scenarios, decision making",
        "Business Scenario Analysis": "Focus on real-world business problems, analysis",
        "Time and Work": "Focus on efficiency, collaboration, time management",
        "Time and Distance": "Focus on speed, time, relative motion problems",
        "Simple Interest": "Focus on basic interest calculations, principal, rate, time",
        "Compound Interest": "Focus on compound growth, multiple periods, calculations",
        "Probability": "Focus on chance, likelihood, combinations, permutations",
        "Permutations and Combinations": "Focus on arrangements, selections, counting",
        "Averages": "Focus on mean calculations, weighted averages, data sets",
        "Partnership": "Focus on business partnerships, profit sharing, investments"
    }
    
    requirements = topic_requirements.get(topic, "Focus on aptitude problem solving")
    
    prompt = f"""
    {level_prompts.get(level, "Generate a scenario question")} for {topic} aptitude.
    
    Topic Focus: {requirements}
    
    Requirements:
    - Create a realistic business/company or practical scenario
    - Provide a clear question with numerical or specific answer
    - Make it suitable for competitive exams
    - Answer should be a single number, percentage, or simple value
    - Include 4 multiple choice options (1 correct, 3 wrong but plausible)
    - Ensure difficulty matches Level {level} complexity
    
    Format your response as JSON:
    {{
        "question": "Your scenario question here",
        "answer": "correct answer",
        "options": ["correct", "wrong1", "wrong2", "wrong3"]
    }}
    """
    
    try:
        response = ask_gemini(prompt)
        
        # Try to extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            import json
            data = json.loads(json_match.group())
            return {
                "q": data.get("question", ""),
                "a": str(data.get("answer", "")),
                "o": [str(opt) for opt in data.get("options", [])],
                "t": topic
            }
        else:
            # Fallback if JSON parsing fails
            return gen_fallback_question(topic, level)
            
    except Exception as e:
        # Fallback if AI fails
        return gen_fallback_question(topic, level)

def gen_fallback_question(topic, level):
    """Fallback question generator when AI fails for ALL topics"""
    
    fallback_questions = {
        "Percentages": {
            1: ("What is 20% of 100?", "20", ["20", "30", "40", "50"]),
            2: ("A product costs $200. With 10% discount, what's price?", "180", ["180", "190", "200", "210"]),
            3: ("Salary was $5000, increased by 15%. New salary?", "5750", ["5750", "5500", "5250", "6000"]),
            4: ("Company revenue $100K grew by 25% then decreased by 10%. Final revenue?", "112500", ["112500", "115000", "110000", "105000"]),
            5: ("Investment $50K grew 20% year 1, lost 15% year 2, gained 25% year 3. Final amount?", "63750", ["63750", "65000", "62500", "60000"])
        },
        "Ratios and Proportions": {
            1: ("Ratio 2:3, total 50. First part?", "20", ["20", "30", "25", "15"]),
            2: ("Partners invest 3:2, profit $5000. First partner's share?", "3000", ["3000", "2000", "2500", "1500"]),
            3: ("Mixture ratio 4:5, total 180L. Quantity of first liquid?", "80", ["80", "100", "90", "70"]),
            4: ("Three partners 2:3:5, investment $200K. Largest share?", "100000", ["100000", "80000", "60000", "40000"]),
            5: ("Complex ratio problem with profit sharing and working hours", "45000", ["45000", "50000", "40000", "35000"])
        },
        "Profit & Loss": {
            1: ("Cost $50, sold for $60. Profit percentage?", "20%", ["20%", "10%", "30%", "25%"]),
            2: ("CP $100, SP $120. Profit %?", "20%", ["20%", "15%", "25%", "30%"]),
            3: ("Markup 25%, discount 10%. Net profit %?", "12.5%", ["12.5%", "15%", "10%", "20%"]),
            4: ("Loss 20%, then gain 30%. Overall result?", "4% gain", ["4% gain", "4% loss", "10% gain", "10% loss"]),
            5: ("Complex profit-loss with multiple transactions", "15.5%", ["15.5%", "16.5%", "14.5%", "17.5%"])
        },
        "Number Systems": {
            1: ("Find HCF of 12 and 18", "6", ["6", "12", "18", "24"]),
            2: ("8-bit binary numbers. How many unique values?", "256", ["256", "128", "512", "64"]),
            3: ("Find LCM of 15, 20, 25", "300", ["300", "150", "75", "600"]),
            4: ("Convert 0.333... to fraction", "1/3", ["1/3", "33/100", "3/10", "1/2"]),
            5: ("Complex number system problem with base conversions", "42", ["42", "36", "48", "54"])
        },
        "Algebra": {
            1: ("Solve: 2x + 5 = 15", "5", ["5", "10", "7", "8"]),
            2: ("Father is 30 years older than son. Sum is 50. Father's age?", "40", ["40", "35", "45", "30"]),
            3: ("If x + y = 10 and x - y = 4, find x", "7", ["7", "6", "8", "5"]),
            4: ("Quadratic: x² - 5x + 6 = 0. Positive root?", "3", ["3", "2", "6", "1"]),
            5: ("Complex word problem with multiple variables", "25", ["25", "20", "30", "35"])
        },
        "Geometry": {
            1: ("Rectangle: length 10m, width 5m. Area?", "50", ["50", "15", "30", "100"]),
            2: ("Circle radius 7m. Area? (π=22/7)", "154", ["154", "44", "22", "308"]),
            3: ("Cube edge 6cm. Surface area?", "216", ["216", "36", "108", "72"]),
            4: ("Cylinder radius 3cm, height 10cm. Volume? (π=3.14)", "282.6", ["282.6", "94.2", "188.4", "314"]),
            5: ("Complex geometry with multiple shapes", "120", ["120", "100", "140", "80"])
        },
        "Time and Work": {
            1: ("A can do work in 10 days. B in 15 days. Together?", "6 days", ["6 days", "8 days", "12 days", "25 days"]),
            2: ("Pipe fills tank in 4 hours, another in 6 hours. Together?", "2.4 hours", ["2.4 hours", "3 hours", "5 hours", "10 hours"]),
            3: ("A works 8 hours/day, B 6 hours/day. Work ratio?", "4:3", ["4:3", "3:4", "2:3", "3:2"]),
            4: ("Complex work problem with efficiency changes", "15 days", ["15 days", "12 days", "18 days", "20 days"]),
            5: ("Very complex work scenario with multiple workers", "8 days", ["8 days", "10 days", "6 days", "12 days"])
        },
        "Data Interpretation": {
            1: ("Sales: Jan=100, Feb=120, Mar=140. Growth % from Jan to Mar?", "40%", ["40%", "20%", "30%", "140%"]),
            2: ("Chart shows A=30%, B=25%, C=20%, D=25%. Which is largest?", "A", ["A", "B", "C", "D"]),
            3: ("Table: Product X=500, Y=300, Z=200. % of X in total?", "50%", ["50%", "30%", "20%", "40%"]),
            4: ("Graph shows increasing trend. What does it indicate?", "Growth", ["Growth", "Decline", "Stability", "Volatility"]),
            5: ("Complex data analysis with multiple variables", "45%", ["45%", "40%", "50%", "35%"])
        },
        "Logical Reasoning": {
            1: ("All cats are animals. Some animals are pets. Conclusion?", "Some cats may be pets", ["Some cats may be pets", "All cats are pets", "No cat is pet", "All pets are cats"]),
            2: ("A is B's brother. C is B's mother. How is C related to A?", "Mother", ["Mother", "Sister", "Aunt", "Grandmother"]),
            3: ("Series: 2, 4, 8, 16, ?", "32", ["32", "24", "20", "64"]),
            4: ("Complex syllogism with multiple statements", "Some A are B", ["Some A are B", "All A are B", "No A is B", "Some B are A"]),
            5: ("Very complex logical puzzle", "D", ["D", "A", "B", "C"])
        },
        "Vocabulary": {
            1: ("Synonym of 'happy'?", "joyful", ["joyful", "sad", "angry", "calm"]),
            2: ("Antonym of 'fast'?", "slow", ["slow", "quick", "rapid", "swift"]),
            3: ("Meaning of 'ubiquitous'?", "everywhere", ["everywhere", "rare", "sometimes", "never"]),
            4: ("Word similar to 'diligent'?", "hardworking", ["hardworking", "lazy", "careless", "quick"]),
            5: ("Complex vocabulary with context", "meticulous", ["meticulous", "careless", "simple", "ordinary"])
        }
    }
    
    # Get fallback for topic and level
    if topic in fallback_questions and level in fallback_questions[topic]:
        q_data = fallback_questions[topic][level]
        return {"q": q_data[0], "a": q_data[1], "o": q_data[2], "t": topic}
    else:
        # Generic fallback
        return {
            "q": f"Solve: {level * 10} + {level * 5} = ?",
            "a": str(level * 15),
            "o": [str(level * 15), str(level * 16), str(level * 14), str(level * 13)],
            "t": topic
        }

def gen_q(category_topic, user_level=3):
    """Generate AI-powered questions for comprehensive aptitude topics"""
    
    # Parse category and topic
    parts = category_topic.split(" - ")
    main_cat = parts[0] if len(parts) > 0 else "Numerical Aptitude"
    topic = parts[1] if len(parts) > 1 else "Percentages"
    
    # Track generated questions for uniqueness
    if "generated_questions" not in st.session_state:
        st.session_state.generated_questions = set()
    
    # Track level-specific questions to prevent repetition across levels
    if "level_questions" not in st.session_state:
        st.session_state.level_questions = {1: set(), 2: set(), 3: set(), 4: set(), 5: set()}
    
    max_attempts = 10
    attempts = 0
    
    while attempts < max_attempts:
        attempts += 1
        
        # Generate AI question
        question_data = gen_ai_question(topic, user_level)
        
        # Check if this question is unique across all levels
        question_key = f"{topic}:{question_data['q'][:50]}"  # First 50 chars as key
        
        is_unique = True
        for level_questions in st.session_state.level_questions.values():
            if question_key in level_questions:
                is_unique = False
                break
        
        if is_unique:
            # Add to current level's question set
            st.session_state.level_questions[user_level].add(question_key)
            st.session_state.generated_questions.add(question_data['q'])
            
            # Ensure 4 options
            if len(question_data['o']) < 4:
                # Add random options
                while len(question_data['o']) < 4:
                    question_data['o'].append(str(random.randint(1, 100)))
            
            # Shuffle options but keep track of correct answer
            correct_ans = question_data['a']
            options = question_data['o'][:4]
            random.shuffle(options)
            
            return {
                "q": question_data['q'], 
                "a": correct_ans, 
                "o": options, 
                "t": topic
            }
    
    # Fallback if AI generation fails
    return gen_fallback_question(topic, user_level)

# ----------- HOME ----------- #
if st.session_state.page=="home":

    st.title(f"Welcome {st.session_state.user}")

    c1,c2,c3 = st.columns(3)

    if c1.button("Start"):
        st.session_state.page="set"; st.rerun()

    if c2.button("Progress"):
        st.session_state.page="progress"; st.rerun()

    if c3.button("Chat"):
        st.session_state.page="chat"; st.rerun()

# ----------- SETTINGS ----------- #
elif st.session_state.page=="set":

    st.title("Select Aptitude Categories")
    
    # Select main categories - empty initially
    available_categories = list(APTITUDE_TOPICS.keys())
    selected_categories = st.multiselect(
        "Select Main Categories", 
        available_categories, 
        default=[]
    )
    
    # Difficulty level indicator with progression info
    current_level = st.session_state.get("user_difficulty_level", 1)
    consecutive_perfect = st.session_state.get("consecutive_perfect_quizzes", 0)
    
    # Required perfect quizzes for each level
    required_map = {1: 3, 2: 3, 3: 4, 4: 5, 5: 0}
    required = required_map.get(current_level, 3)
    
    st.subheader(f"🎯 Level {current_level}/5")
    
    if current_level < 5:
        st.info(f"📈 Need {required} consecutive PERFECT (100%) quizzes to advance to Level {current_level + 1}")
        st.write(f"Current streak: {consecutive_perfect}/{required}")
        st.progress(min(consecutive_perfect / required, 1.0))
    else:
        st.success("🏆 MASTER LEVEL ACHIEVED! Perfect performance!")
    
    n=st.number_input("Questions (5-50)",5,50,10)

    if st.button("Start Quiz"):
        if not selected_categories:
            st.error("Please select at least one category")
        else:
            user["count"]+=1
            quiz = []
            # Clear generated questions tracker for new quiz
            st.session_state.generated_questions = set()
            
            # Get all sub-topics from selected categories
            available_subtopics = []
            for cat in selected_categories:
                for subtopic in APTITUDE_TOPICS[cat].keys():
                    available_subtopics.append(f"{cat} - {subtopic}")
            
            # Generate questions with adaptive difficulty
            for _ in range(n):
                category_topic = random.choice(available_subtopics)
                quiz.append(gen_q(category_topic, current_level))
            
            # Shuffle questions
            random.shuffle(quiz)
            st.session_state.quiz = quiz
            st.session_state.ans=[None]*n
            st.session_state.cur=0
            st.session_state.start=time.time()
            st.session_state.selected_categories = selected_categories
            save(users)
            st.session_state.page="quiz"
            st.rerun()

# ----------- QUIZ ----------- #
elif st.session_state.page=="quiz":

    # Safety check - ensure quiz exists and has questions
    if not st.session_state.quiz or len(st.session_state.quiz) == 0:
        st.error("No quiz questions available. Please start a new quiz.")
        if st.button("Go to Settings"):
            st.session_state.page="set"
            st.rerun()
        st.stop()

    total=len(st.session_state.quiz)*30
    left=max(0,total-int(time.time()-st.session_state.start))
    st.warning(f"Time Left: {left}s")

    i=st.session_state.cur
    
    # Bounds checking for current index
    if i >= len(st.session_state.quiz):
        i = len(st.session_state.quiz) - 1
        st.session_state.cur = i
    
    q=st.session_state.quiz[i]
    ans=st.session_state.ans

    c1,c2,c3=st.columns(3)
    c1.metric("Attempted",sum(1 for x in ans if x))
    c2.metric("Not Attempted",len(ans)-sum(1 for x in ans if x))
    c3.metric("Remaining",len(ans)-i)

    st.write(f"Q{i+1}: {q['q']}")
    
    # Use form to handle quiz submission properly
    with st.form(key=f"quiz_form_{i}"):
        choice=st.radio("Select your answer:",["--Select--"]+q["o"],key=f"q{i}")
        col1,col2=st.columns(2)
        with col1:
            prev_clicked = st.form_submit_button("Previous") if i > 0 else None
        with col2:
            next_clicked = st.form_submit_button("Next")
    
    # Handle form submission outside the form
    if prev_clicked:
        st.session_state.cur -= 1
        st.rerun()

    if next_clicked:
        if choice != "--Select--":
            st.session_state.ans[i] = choice
        st.session_state.cur += 1
        # Check if we've reached the end of quiz
        if st.session_state.cur >= len(st.session_state.quiz):
            st.session_state.page = "result"
        st.rerun()

# ----------- RESULT ----------- #
elif st.session_state.page=="result":

    score=0
    correct_count = 0
    incorrect_count = 0

    for i,q in enumerate(st.session_state.quiz):
        user["perf"].setdefault(q["t"],{"c":0,"w":0})

        if st.session_state.ans[i]==q['a']:
            score+=1
            correct_count += 1
            user["perf"][q["t"]]["c"]+=1
        else:
            incorrect_count += 1
            user["perf"][q["t"]]["w"]+=1

    # Update adaptive difficulty based on consecutive perfect quizzes
    current_level = st.session_state.get("user_difficulty_level", 1)
    accuracy = correct_count / len(st.session_state.quiz) if st.session_state.quiz else 0
    is_perfect = (accuracy == 1.0)
    
    # Track total quizzes at current level
    if "total_quizzes_at_level" not in st.session_state:
        st.session_state.total_quizzes_at_level = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    st.session_state.total_quizzes_at_level[current_level] += 1
    
    if is_perfect:
        # Increment consecutive perfect counter
        st.session_state.consecutive_perfect_quizzes += 1
        
        # Check if ready to level up
        required_consecutive = current_level + 2  # Level 1 needs 3, Level 2 needs 3, Level 3 needs 4, Level 4 needs 5
        if current_level == 1:
            required_consecutive = 3  # Need 3 perfect quizzes to reach Level 2
        elif current_level == 2:
            required_consecutive = 3  # Need 3 perfect quizzes to reach Level 3
        elif current_level == 3:
            required_consecutive = 4  # Need 4 perfect quizzes to reach Level 4
        elif current_level == 4:
            required_consecutive = 5  # Need 5 perfect quizzes to reach Level 5
        
        if st.session_state.consecutive_perfect_quizzes >= required_consecutive and current_level < 5:
            new_level = current_level + 1
            st.session_state.user_difficulty_level = new_level
            st.session_state.consecutive_perfect_quizzes = 0  # Reset for next level
            st.success(f"🎉 MASTERED Level {current_level}! Advanced to Level {new_level}/5")
        else:
            remaining = required_consecutive - st.session_state.consecutive_perfect_quizzes
            st.info(f"� Perfect! Level {current_level}/5 - Need {remaining} more perfect quiz to advance")
    else:
        # Reset consecutive counter if not perfect
        if st.session_state.consecutive_perfect_quizzes > 0:
            st.warning(f"📚 Streak broken! Need {required_consecutive} consecutive perfect quizzes at Level {current_level}")
        st.session_state.consecutive_perfect_quizzes = 0
        st.info(f"📊 Score: {int(accuracy*100)}% - Practice more to master Level {current_level}/5")

    save(users)

    st.markdown(f"# 🎯 Score: {score}/{len(st.session_state.quiz)} ({int(accuracy*100)}%)")

    for i,q in enumerate(st.session_state.quiz):
        st.write(f"**Q{i+1}:** {q['q']}")
        user_ans = st.session_state.ans[i] if st.session_state.ans[i] else "Not answered"
        if st.session_state.ans[i]==q['a']:
            st.success(f"✓ Your answer: {user_ans} | Correct answer: {q['a']}")
        else:
            st.error(f"✗ Your answer: {user_ans} | Correct answer: {q['a']}")
        st.write("---")

    if st.button("Restart"):
        st.session_state.page="home"; st.rerun()

    if st.button("Exit"):
        st.session_state.login=False
        st.session_state.page=""
        st.rerun()

# ----------- PROGRESS ----------- #
elif st.session_state.page=="progress":

    st.title("📊 Your Progress")
    
    # Show current adaptive difficulty level
    current_level = st.session_state.get("user_difficulty_level", 1)
    consecutive_perfect = st.session_state.get("consecutive_perfect_quizzes", 0)
    
    # Calculate required for next level
    if current_level == 1:
        required = 3
    elif current_level == 2:
        required = 3
    elif current_level == 3:
        required = 4
    elif current_level == 4:
        required = 5
    else:
        required = 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Level", f"{current_level}/5")
    col2.metric("Perfect Streak", f"{consecutive_perfect}/{required}")
    col3.metric("Total Quizzes", user["count"])
    
    # Progress bar for next level
    if required > 0:
        progress = min(consecutive_perfect / required, 1.0)
        st.write(f"**Progress to Level {current_level + 1}:**")
        st.progress(progress)
        if consecutive_perfect > 0:
            st.info(f"Need {required - consecutive_perfect} more perfect quiz to advance")
    else:
        st.success("🎉 MAX LEVEL REACHED! You are an Aptitude Master!")
    
    # Organize performance by main categories
    if user["perf"]:
        # Group by main category
        category_perf = {}
        for topic, data in user["perf"].items():
            # Extract main category from topic string
            main_cat = topic.split(" - ")[0] if " - " in topic else "Other"
            if main_cat not in category_perf:
                category_perf[main_cat] = {"c": 0, "w": 0}
            category_perf[main_cat]["c"] += data["c"]
            category_perf[main_cat]["w"] += data["w"]
        
        # Display by category
        for cat, data in category_perf.items():
            total = data["c"] + data["w"]
            if total > 0:
                p = int(data["c"] / total * 100)
                st.write(f"**{cat}:** {p}% ({data['c']}/{total} correct)")
                st.progress(p/100)
        
        # Show detailed breakdown
        st.write("---")
        st.write("**Detailed Topic Performance:**")
        for t, d in sorted(user["perf"].items()):
            total = d["c"] + d["w"]
            if total > 0:
                p = int(d["c"] / total * 100)
                st.write(f"• {t}: {p}%")
    else:
        st.info("No quiz data yet. Start a quiz to track your progress!")

    if st.button("Back"):
        st.session_state.page="home"; st.rerun()

# ----------- CHAT ----------- #
elif st.session_state.page=="chat":

    st.title("AI Chat")

    if "chat" not in st.session_state:
        st.session_state.chat=[]

    for m in st.session_state.chat:
        st.write(m)

    # Use a form to handle both button and Enter key submission
    with st.form(key="chat_form", clear_on_submit=True):
        msg = st.text_input("Ask aptitude", key="chat_input_field")
        # Row 1: Send on the right below message box
        c1, c2 = st.columns([3, 1])
        with c2:
            send_clicked = st.form_submit_button("Send")
        # Row 2: Exit on the left side below Send
        c3, c4 = st.columns([1, 3])
        with c3:
            exit_clicked = st.form_submit_button("Exit")

    if exit_clicked:
        st.session_state.page="home"
        st.rerun()

    if send_clicked and msg:
        st.session_state.chat.append("You: "+msg)
        reply=ask_gemini(msg)
        st.session_state.chat.append("Bot: "+reply)
        st.rerun()

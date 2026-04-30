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
    json.dump(d, open(FILE, "w"))

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

def gen_q(category_topic, user_level=3):
    """Generate scenario-based questions for comprehensive aptitude topics with adaptive difficulty"""
    
    # Parse category and topic
    parts = category_topic.split(" - ")
    main_cat = parts[0] if len(parts) > 0 else "Numerical Aptitude"
    topic = parts[1] if len(parts) > 1 else "Percentages"
    
    params = get_difficulty_params(user_level)
    low, high = params["numbers"]
    
    # Track generated questions for uniqueness
    if "generated_questions" not in st.session_state:
        st.session_state.generated_questions = set()
    
    max_attempts = 50
    attempts = 0
    
    while attempts < max_attempts:
        attempts += 1
        q, ans, o = None, None, []
        
        # NUMERICAL APTITUDE
        if topic == "Number Systems":
            scenarios = [
                ("A computer system uses ", "-bit binary numbers. How many unique addresses can it represent?"),
                ("Find the LCM of ", " and ", " for scheduling two machines."),
                ("In a library, books are arranged in groups of ", ". If there are ", " books total, how many complete groups?"),
                ("A password uses ", " characters from ", " symbols. Total combinations?")
            ]
            if params["complexity"] == "basic":
                a, b = random.randint(2, 20), random.randint(2, 20)
                q = f"Find the HCF of {a} and {b}."
                import math
                ans = str(math.gcd(a, b))
                o = [ans, str(a), str(b), str((a+b)//2)]
            else:
                bits = random.choice([8, 16, 32])
                q = f"A computer system uses {bits}-bit binary numbers. How many unique addresses can it represent?"
                ans = str(2**bits)
                o = [ans, str(2**(bits-1)), str(2**(bits+1)), str(bits**2)]
                
        elif topic == "Fractions and Decimals":
            if params["complexity"] == "basic":
                a, b = random.randint(1, 9), random.randint(2, 9)
                q = f"A recipe needs {a}/{b} cup of sugar. For {random.randint(2,5)} batches, how much sugar total?"
                total = a * random.randint(2,5)
                ans = f"{total}/{b}"
                o = [ans, f"{total}/{b+1}", f"{total+1}/{b}", f"{a}/{b*2}"]
            else:
                d = random.choice([3, 6, 7, 9])
                q = f"Convert 0.{str(d)*3}... to a fraction (recurring decimal)."
                ans = f"{d}/9"
                o = [ans, f"{d}/10", f"1/{d}", f"{d+1}/9"]
                
        elif topic == "Percentages":
            scenarios = [
                ("Company revenue was $", "M last year. With ", "% growth this year, what's the new revenue?"),
                ("An employee earning $", "K gets a ", "% raise. New salary?"),
                ("A $", " item has ", "% discount then ", "% tax. Final price?"),
                ("Population: ", " people, growing at ", "% annually. After 2 years?")
            ]
            base = random.choice([50000, 100000, 250000, 500000])
            pct = random.randint(10, 30)
            if params["multi_step"]:
                tax = random.randint(5, 18)
                q = f"A ${base} laptop has {pct}% discount, then {tax}% tax. Final price?"
                discounted = base * (100 - pct) / 100
                final = discounted * (100 + tax) / 100
                ans = f"${int(final)}"
                o = [ans, f"${int(final+500)}", f"${int(final-500)}", f"${int(base * 0.9)}"]
            else:
                q = f"Company revenue was ${base} last year. With {pct}% growth, new revenue?"
                new_rev = int(base * (100 + pct) / 100)
                ans = f"${new_rev}"
                o = [ans, f"${new_rev+1000}", f"${int(base * pct / 100)}", f"${base+pct}"]

        elif topic == "Ratios and Proportions":
            scenarios = [
                ("Partners A and B invest in ratio ", ":", ". Profit $", " - A's share?"),
                ("Mixture: liquid A to B is ", ":", ". Total ", "L. Quantity of A?"),
                ("Map scale 1:", ". Real distance ", "km. Map distance in cm?"),
                ("Division: $", " among 3 people in ratio ", ":", ":", " - largest share?")
            ]
            if params["complexity"] == "advanced":
                a, b, c = 2, 3, 5
                total = random.choice([10000, 20000, 50000])
                q = f"Three partners invest in ratio {a}:{b}:{c}. Total investment ${total}. Largest share?"
                largest = total * max(a,b,c) / (a+b+c)
                ans = f"${int(largest)}"
                o = [ans, f"${int(total/3)}", f"${int(total * 0.5)}", f"${int(total * 0.4)}"]
            else:
                a, b = 2, 3
                total = random.randint(50, 200)
                q = f"Mixture ratio {a}:{b}, total {total}L. Quantity of first liquid?"
                qty = int(total * a / (a + b))
                ans = f"{qty}L"
                o = [ans, f"{total - qty}L", f"{total//2}L", f"{qty+5}L"]

        elif topic == "Algebra":
            if params["complexity"] == "basic":
                a = random.randint(2, 5)
                b = random.randint(10, 30)
                q = f"Solve: {a}x + {b//a} = {b + random.randint(5,15)}. Find x."
                ans = str(random.randint(2, 6))
                o = [ans, str(int(ans)+1), str(int(ans)-1), str(int(ans)*2)]
            else:
                age_diff = random.randint(5, 15)
                sum_age = random.randint(40, 80)
                q = f"Father is {age_diff} years older than son. Sum of ages is {sum_age}. Father's age?"
                father = (sum_age + age_diff) // 2
                ans = str(father)
                o = [ans, str(father + 5), str(father - 5), str(sum_age // 2)]

        elif topic == "Geometry":
            scenarios = [
                ("Rectangular field: length ", "m, breadth ", "m. Area and cost at $", "/sq m?"),
                ("Circular pond: radius ", "m. Fence cost at $", "/meter?"),
                ("Cube: edge ", "cm. Volume and surface area?"),
                ("Cylinder: radius ", "cm, height ", "cm. Volume?")
            ]
            if "Rectangular" in scenarios[0][0]:
                l, b = random.randint(20, 100), random.randint(15, 60)
                rate = random.randint(5, 15)
                q = f"Rectangular field: length {l}m, breadth {b}m. Cost to fence at ${rate}/meter?"
                perimeter = 2 * (l + b)
                cost = perimeter * rate
                ans = f"${cost}"
                o = [ans, f"${l*b*rate}", f"${(l+b)*rate}", f"${cost+100}"]
            else:
                r = random.randint(5, 20)
                q = f"Circular garden: radius {r}m. Area for planting?"
                area = int(3.14159 * r * r)
                ans = f"{area} sq m"
                o = [ans, f"{int(2*3.14159*r)} sq m", f"{r*r} sq m", f"{2*area} sq m"]

        elif topic == "Trigonometry":
            height = random.randint(30, 100)
            angle = random.choice([30, 45, 60])
            q = f"Building height {height}m. Sun angle {angle}°. Shadow length?"
            import math
            if angle == 30:
                shadow = int(height * 1.732)
            elif angle == 45:
                shadow = height
            else:
                shadow = int(height / 1.732)
            ans = f"{shadow}m"
            o = [ans, f"{shadow+10}m", f"{int(height/2)}m", f"{height}m"]

        elif topic == "Statistics":
            if params["complexity"] == "basic":
                scores = [random.randint(60, 95) for _ in range(5)]
                q = f"Test scores: {scores}. Mean score?"
                mean = sum(scores) // len(scores)
                ans = str(mean)
                o = [ans, str(max(scores)), str(min(scores)), str((max(scores)+min(scores))//2)]
            else:
                n = random.randint(10, 20)
                total = random.randint(500, 1000)
                mean = total // n
                new_mean = mean + random.randint(2, 5)
                q = f"{n} students average {mean}. New student joins, average becomes {new_mean}. New student's marks?"
                new_total = new_mean * (n + 1)
                new_student = new_total - total
                ans = str(new_student)
                o = [ans, str(new_mean), str(mean + new_mean), str(total // (n+1))]

        elif topic == "Data Interpretation":
            # Simulate chart reading
            categories = ["Product A", "Product B", "Product C", "Product D"]
            values = [random.randint(20, 80) for _ in range(4)]
            total = sum(values)
            q = f"Sales chart (units): A={values[0]}, B={values[1]}, C={values[2]}, D={values[3]}. What % is Product A of total?"
            pct = int(values[0] * 100 / total)
            ans = f"{pct}%"
            o = [ans, f"{values[0]}%", f"{int(values[0]*100/max(values))}%", f"{25}%"]

        # VERBAL APTITUDE
        elif topic == "Vocabulary":
            words = {
                "happy": ["joyful", "sad", "angry", "calm"],
                "fast": ["quick", "slow", "steady", "rapid"],
                "big": ["large", "small", "tiny", "huge"]
            }
            word = random.choice(list(words.keys()))
            w_type = random.choice(["synonym", "antonym"])
            if w_type == "synonym":
                q = f"Select the synonym for '{word}'."
                ans = words[word][0]
            else:
                q = f"Select the antonym for '{word}'."
                ans = words[word][1]
            o = words[word]
            random.shuffle(o)

        elif topic == "Reading Comprehension":
            passages = [
                "A company implemented AI to improve customer service. Response times decreased by 40% while satisfaction scores increased by 25%. However, 15% of staff were reassigned.",
                "Research shows that remote work increases productivity by 13% on average. Employees report higher satisfaction but face challenges with work-life boundaries."
            ]
            passage = random.choice(passages)
            questions = [
                ("What was the main outcome mentioned?", "Productivity improvement" if "productivity" in passage else "Service improvement", ["Cost reduction", "Staff increase", "Service improvement", "Productivity improvement"]),
                ("What challenge is mentioned?", "Work-life balance" if "remote" in passage else "Staff reassignment", ["Technology failure", "Staff reassignment", "Budget issues", "Work-life balance"])
            ]
            q_data = random.choice(questions)
            q = f"Passage: '{passage[:50]}...' Question: {q_data[0]}"
            ans = q_data[1]
            o = q_data[2]

        elif topic == "Grammar":
            errors = [
                ("The team are working on the project.", "The team is working on the project.", "Subject-verb agreement"),
                ("She don't like coffee.", "She doesn't like coffee.", "Auxiliary verb"),
                ("Between you and I, this is wrong.", "Between you and me, this is wrong.", "Pronoun case")
            ]
            err = random.choice(errors)
            q = f"Find the error: '{err[0]}' What type?"
            ans = err[2]
            o = [err[2], "Tense error", "Article error", "Preposition error"]

        elif topic == "Analogies":
            analogies = [
                ("Book : Read :: Food : ?", "Eat", ["Cook", "Eat", "Buy", "Serve"]),
                ("Doctor : Hospital :: Teacher : ?", "School", ["Classroom", "School", "Book", "Student"]),
                ("Car : Road :: Boat : ?", "Water", ["Sea", "River", "Water", "Ocean"])
            ]
            an = random.choice(analogies)
            q = an[0]
            ans = an[1]
            o = an[2]

        # LOGICAL REASONING
        elif topic == "Blood Relations":
            relations = [
                ("A is B's father's only daughter. How is A related to B?", "Sister", ["Mother", "Sister", "Aunt", "Cousin"]),
                ("Pointing to a photo: 'His father is my father's son.' Who is in the photo?", "Son", ["Brother", "Son", "Father", "Uncle"]),
                ("If P's mother is Q's father's sister, how is Q related to P?", "Cousin", ["Brother", "Sister", "Cousin", "Uncle"])
            ]
            rel = random.choice(relations)
            q = rel[0]
            ans = rel[1]
            o = rel[2]

        elif topic == "Coding and Decoding":
            coding = [
                ("If TEACHER is coded as UFBDIIFS, how is STUDENT coded?", "TUVEFOU", ["TUVEFOU", "TSVCFOU", "TUVFNOU", "TTUDFOU"]),
                ("In a code, CAT = 312, DOG = 4157. What is FISH?", "6918", ["6918", "69108", "6819", "69108"])
            ]
            code = random.choice(coding)
            q = code[0]
            ans = code[1]
            o = code[2]

        elif topic == "Directions and Distances":
            dirs = [
                ("Walk 5km north, 3km east, 5km south. Distance from start?", "3km", ["3km", "5km", "8km", "13km"]),
                ("Facing east, turn right, then 180°. Final direction?", "West", ["North", "South", "East", "West"])
            ]
            d = random.choice(dirs)
            q = d[0]
            ans = d[1]
            o = d[2]

        elif topic == "Syllogisms" or topic == "Deductive Reasoning":
            syllogisms = [
                ("All managers are leaders. Some leaders are innovators. Conclusion?", "Some managers may be innovators", ["All managers are innovators", "Some managers may be innovators", "No manager is innovator", "All innovators are managers"]),
                ("No laptop is a phone. All phones are smart devices. Conclusion?", "Some smart devices are not laptops", ["All smart devices are laptops", "Some smart devices are not laptops", "No smart device is laptop", "All laptops are smart devices"])
            ]
            syl = random.choice(syllogisms)
            q = syl[0]
            ans = syl[1]
            o = syl[2]

        elif topic == "Inductive Reasoning":
            series = [
                ("2, 6, 12, 20, 30, ?", "42", ["36", "40", "42", "44"]),
                ("1, 1, 2, 3, 5, 8, ?", "13", ["11", "12", "13", "14"]),
                ("A, C, E, G, ?", "I", ["H", "I", "J", "K"])
            ]
            ser = random.choice(series)
            q = f"Complete the series: {ser[0]}"
            ans = ser[1]
            o = ser[2]

        # NON-VERBAL APTITUDE
        elif topic in ["Visual Reasoning", "Pattern Recognition", "Abstract Reasoning"]:
            patterns = [
                ("Shape sequence: Triangle → Square → Pentagon → ?", "Hexagon", ["Circle", "Hexagon", "Octagon", "Rectangle"]),
                ("Rotation: 90° → 180° → 270° → ?", "360°", ["300°", "360°", "45°", "0°"]),
                ("Number of sides: 3, 4, 5, 6, ?", "7", ["6", "7", "8", "9"])
            ]
            pat = random.choice(patterns)
            q = pat[0]
            ans = pat[1]
            o = pat[2]

        elif topic in ["Spatial Reasoning", "Paper Folding and Cutting"]:
            spatial = [
                ("Cube has how many faces?", "6", ["4", "5", "6", "8"]),
                ("Paper folded twice, one hole punched. How many holes when unfolded?", "4", ["2", "3", "4", "1"]),
                ("Cylinder: radius 3cm, height 10cm. Volume? (π=3.14)", "282.6", ["282.6", "188.4", "94.2", "314"])
            ]
            sp = random.choice(spatial)
            q = sp[0]
            ans = sp[1]
            o = sp[2]

        elif topic == "Mirror Images":
            mirrors = [
                ("Mirror shows 3:15. Real time?", "8:45", ["8:45", "9:45", "3:15", "2:45"]),
                ("Word 'MUM' in mirror looks like?", "MUM", ["MUM", "MWM", "WUW", "WOW"])
            ]
            mir = random.choice(mirrors)
            q = mir[0]
            ans = mir[1]
            o = mir[2]

        # DATA ANALYSIS
        elif topic == "Data Sufficiency":
            sufficiency = [
                ("Is x > y? (1) x² > y² (2) x > 0", "Both together", ["Statement 1 alone", "Statement 2 alone", "Both together", "Neither"]),
                ("What is A's age? (1) B is 5 years older (2) C is 10 years younger than B", "Both together", ["Statement 1 alone", "Statement 2 alone", "Both together", "Neither"])
            ]
            suff = random.choice(sufficiency)
            q = suff[0]
            ans = suff[1]
            o = suff[2]

        elif topic in ["Data Visualization", "Graphical Analysis", "Table Analysis"]:
            # Create realistic data analysis scenario
            months = ["Jan", "Feb", "Mar", "Apr", "May"]
            sales = [random.randint(100, 200) for _ in range(5)]
            q = f"Sales data (units): {dict(zip(months, sales))}. Which month had {max(sales)}% of peak sales?"
            peak = max(sales)
            target = int(peak * 0.8)
            closest_month = months[sales.index(min(sales, key=lambda x: abs(x - target)))]
            ans = closest_month
            o = months

        elif topic == "Statistical Analysis" or topic == "Data Mining":
            stats = [
                (f"Dataset: {[random.randint(10,50) for _ in range(6)]}. Range?", "calculate", "range"),
                (f"Coin tossed 3 times. Probability of 2 heads?", "3/8", ["3/8", "1/2", "1/4", "3/4"])
            ]
            stat = random.choice(stats)
            if stat[2] == "range":
                data = [random.randint(10, 50) for _ in range(6)]
                q = f"Dataset: {data}. What is the range?"
                ans = str(max(data) - min(data))
                o = [ans, str(max(data)), str(min(data)), str(sum(data)//len(data))]
            else:
                q = stat[0]
                ans = stat[1]
                o = stat[2] if len(stat) > 2 else ["3/8", "1/2", "1/4", "3/4"]

        elif topic in ["Case Studies", "Business Scenario Analysis"]:
            business = [
                ("Company: Revenue $1M, Costs $750K. Profit margin?", "25%", ["25%", "33%", "20%", "75%"]),
                ("Break-even: Fixed cost $50000, Unit cost $10, Price $25. Break-even units?", "3333", ["2000", "3333", "5000", "2500"]),
                ("ROI: Invest $100K, Return $125K in 2 years. Annual ROI?", "12.5%", ["25%", "12.5%", "10%", "20%"])
            ]
            biz = random.choice(business)
            q = biz[0]
            ans = biz[1]
            o = biz[2]

        # Fallback
        else:
            q = f"Solve: {random.randint(10, 50)} + {random.randint(20, 80)} = ?"
            ans = str(int(q.split()[1]) + int(q.split()[3]))
            o = [ans, str(int(ans)+10), str(int(ans)-10), str(int(ans)+5)]

        # Ensure uniqueness
        if q and q not in st.session_state.generated_questions:
            st.session_state.generated_questions.add(q)
            o = list(set(o))
            while len(o) < 4:
                o.append(str(random.randint(1, 100)))
            random.shuffle(o)
            return {"q": q, "a": ans, "o": o[:4], "t": topic}
    
    # Fallback if unique question not found
    q = f"Calculate: {random.randint(10, 99)} × {random.randint(2, 9)} = ?"
    ans = str(eval(q.split()[1]) * eval(q.split()[3]))
    o = [ans, str(int(ans)+10), str(int(ans)-10), str(int(ans)*2)]
    random.shuffle(o)
    return {"q": q, "a": ans, "o": o, "t": topic}

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

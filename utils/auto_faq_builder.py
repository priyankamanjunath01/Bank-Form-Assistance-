import re
import json
import os
import spacy

# Load spaCy model for lemmatization
nlp = spacy.load("en_core_web_sm")

faq_patterns = {
    "form 60": "What is Form 60?",
    "form 16": "What is Form 16?",
    "pan card": "Is PAN card mandatory?",
    "aadhaar": "What is Aadhaar linking?",
    "kyc": "What is KYC document?",
    "passport size photo": "Why is a passport size photo required?",
    "applicant name": "What is applicant name section?",
    "guardian": "Who is considered a guardian?",
    "minor": "How to open account for a minor?",
    "joint holder": "What is a joint account?",
    "nominee": "Who is a nominee?",
    "nomination": "What is the nomination facility?",
    "gender": "What should I select for gender?",
    "marital status": "Why is marital status needed?",
    "occupation": "How to fill occupation details?",
    "income": "What is the income range used for?",
    "politically exposed": "What does politically exposed person mean?",
    "communication address": "What is the communication address section for?",
    "permanent address": "What is the permanent address?",
    "mobile number": "Is a mobile number mandatory?",
    "email": "Why is email ID required?",
    "signature": "Where should I sign on the form?",
    "document proof": "What documents are accepted as proof?",
    "photo id proof": "What is a valid photo ID proof?",
    "address proof": "What is considered valid address proof?",
    "bsbda": "What is a BSBDA account?",
    "fd account": "What is an FD account?",
    "rd account": "What is an RD account?",
    "savings account": "What is a savings account?",
    "current account": "What is a current account?",
    "personal details": "What are personal details?",
    "occupation type": "What are the occupation types?",
    "annual income": "Why is annual income information required?",
    "education": "Is education qualification required?",
    "minor declaration": "What is minor declaration form?"
}

fallback_answers = {
    "form 60": "Form 60 is submitted by individuals who do not have a PAN card but wish to open a bank account.",
    "form 16": "Form 16 is a certificate issued by an employer showing the tax deducted at source.",
    "pan card":"PAN card is mandatory for financial transactions. If unavailable, Form 60 can be used.",
    "aadhaar": "Aadhaar linking refers to attaching your UIDAI number to your bank account.",
    "kyc": "KYC stands for Know Your Customer, a mandatory identification process.",
    "passport size photo": "A passport photo is required for identification purposes in bank forms.",
    "applicant name": "This section should contain your full legal name as per your identity documents.",
    "guardian": "A guardian is a legal adult who handles the account on behalf of a minor.",
    "minor": "To open an account for a minor, guardian details and minor declaration form are needed.",
    "joint holder": "A joint account allows more than one person to operate the account.",
    "nominee": "A nominee is someone who receives account funds in the event of the account holder's death.",
    "nomination": "Nomination is an option to assign someone to receive the funds if the account holder passes away.",
    "gender": "Choose Male, Female, or Other based on your gender identity.",
    "marital status": "This is required for demographic profiling and service customization.",
    "occupation": "Mention your current employment type: salaried, self-employed, student, etc.",
    "income": "This helps the bank understand your financial profile.",
    "politically exposed": "A politically exposed person (PEP) holds a prominent public position such as MP or MLA.",
    "communication address": "This is the address where you want to receive all bank correspondence.",
    "permanent address": "Your fixed, long-term address, usually the one on your government ID.",
    "mobile number": "It is mandatory to receive transaction alerts and OTPs.",
    "email": "Used for sending e-statements and service notifications.",
    "signature": "Sign clearly within the specified space to validate your application.",
    "document proof": "You can use Aadhaar, Passport, Voter ID, Driving License, or Utility Bills.",
    "photo id proof": "Acceptable ID proof includes Aadhaar, Passport, PAN card, or Driving License.",
    "address proof": "Accepted proofs include Aadhaar, utility bills, rental agreements, etc.",
    "bsbda": "BSBDA stands for Basic Savings Bank Deposit Account with minimum service.",
    "fd account": "FD stands for Fixed Deposit – a term deposit that earns higher interest.",
    "rd account": "RD stands for Recurring Deposit – you deposit a fixed amount monthly.",
    "savings account": "A savings account is used for regular deposits, withdrawals, and interest earnings.",
    "current account": "Designed for businesses with high volume transactions, no interest is paid.",
    "personal details": "These include your full name, DOB, contact number, and address.",
    "occupation type": "Select one of: Salaried, Self-Employed, Student, Retired, Housewife, etc.",
    "annual income": "Income details help the bank assess your financial status and offer products.",
    "education": "Some banks may collect this for demographic analysis but it is often optional.",
    "minor declaration": "A form signed by the guardian declaring their relationship with the minor."
}

def generate_faq_from_text(cleaned_text, output_path="output/faq_knowledge.json"):
    # Lemmatize the text
    doc = nlp(cleaned_text.lower())
    lemmatized_text = " ".join([token.lemma_ for token in doc if not token.is_punct])

    faqs = []

    for keyword, question in faq_patterns.items():
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, lemmatized_text):
            answer = fallback_answers.get(keyword, "Answer not available.")
            faqs.append({
                "question": question,
                "answer": answer
            })
        else:
            print(f"[!] Keyword '{keyword}' not found in text — using fallback answer.")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(faqs, f, indent=4)

    print(f" FAQ saved to: {output_path}")

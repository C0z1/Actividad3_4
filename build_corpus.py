"""
build_corpus.py
---------------
Generates `corpus.csv`, the document repository used by the recommender system
(Activity 3) and its evaluation (Activity 4).

The corpus mixes two document families requested by the assignment:
  * "Public"-style documents  -> short articles / company news.
  * "Simulated" documents      -> fictional internal policies, meeting minutes,
                                  FAQs and support tickets/incidents.

Each document is defined once, as a plain Python dict, which keeps the text
readable and free of CSV-escaping mistakes. The script then writes a clean
`corpus.csv` with the exact columns the assignment asks for:

    id, title, text, category

Run it with:

    python build_corpus.py
"""

from __future__ import annotations

import csv
from pathlib import Path

# ---------------------------------------------------------------------------
# Document definitions.
#
# Categories are intentionally overlapping in vocabulary (e.g. "VPN", "security",
# "password") so that the recommender has to rely on real term statistics rather
# than trivial keyword matches. This makes the later evaluation meaningful.
# ---------------------------------------------------------------------------
DOCUMENTS: list[dict[str, str]] = [
    # ================= POLICY / PROCESS (simulated internal documents) =======
    {
        "id": "DOC001",
        "title": "Remote Work Policy",
        "category": "Policy/Process",
        "text": (
            "This policy defines how employees may work remotely. Staff can work "
            "from home up to three days per week with manager approval. Remote "
            "employees must keep a stable internet connection, stay reachable "
            "during core hours, and use the company VPN whenever they access "
            "internal systems. Equipment provided for home use remains company "
            "property and must be returned when employment ends. Managers are "
            "responsible for tracking attendance and ensuring fair treatment "
            "between on-site and remote team members."
        ),
    },
    {
        "id": "DOC002",
        "title": "Expense Reimbursement Procedure",
        "category": "Policy/Process",
        "text": (
            "Employees who incur business expenses may request reimbursement "
            "through the finance portal. Receipts must be submitted within thirty "
            "days of purchase. Approved categories include travel, lodging, client "
            "meals, and software subscriptions. Expenses above five hundred dollars "
            "require prior written approval from a department head. Reimbursements "
            "are processed in the next payroll cycle after the manager approves the "
            "request. Fraudulent or duplicate claims are grounds for disciplinary "
            "action."
        ),
    },
    {
        "id": "DOC003",
        "title": "Data Retention and Deletion Policy",
        "category": "Policy/Process",
        "text": (
            "This policy governs how long the organization stores different types "
            "of data. Customer records are retained for seven years to satisfy "
            "legal and tax obligations. Internal logs and temporary files are kept "
            "for ninety days and then deleted automatically. Personal data must be "
            "removed on request in line with privacy regulations. Backups are "
            "encrypted and rotated monthly. Teams must not store sensitive data on "
            "personal devices or in unapproved cloud services."
        ),
    },
    {
        "id": "DOC004",
        "title": "Employee Onboarding Process",
        "category": "Policy/Process",
        "text": (
            "The onboarding process ensures that new hires become productive "
            "quickly. On the first day, IT provisions a laptop, email account, and "
            "access to core systems. Human resources reviews benefits, payroll, and "
            "workplace policies. Each new employee is assigned a mentor for the "
            "first ninety days. A structured checklist covers security training, "
            "tool setup, and introductions to key stakeholders. Managers schedule a "
            "thirty-day review to confirm the new hire has the resources they need."
        ),
    },
    {
        "id": "DOC005",
        "title": "Information Security Policy",
        "category": "Policy/Process",
        "text": (
            "All employees must protect company information from unauthorized "
            "access. Passwords must be at least twelve characters and changed every "
            "ninety days. Multi-factor authentication is mandatory for email and "
            "remote access through the VPN. Staff must lock their screens when away "
            "from their desks and report any suspected phishing or data breach "
            "immediately. Access to sensitive systems follows the principle of least "
            "privilege, granting only the permissions required for a role."
        ),
    },
    {
        "id": "DOC006",
        "title": "Paid Time Off Policy",
        "category": "Policy/Process",
        "text": (
            "Full-time employees accrue paid time off based on tenure. Staff with "
            "fewer than three years of service earn fifteen days per year, while "
            "those with more earn twenty. Time off must be requested at least two "
            "weeks in advance through the human resources portal and approved by a "
            "manager. Unused days may roll over up to a maximum of five days into "
            "the following year. Sick leave is tracked separately and does not count "
            "against the vacation balance."
        ),
    },
    {
        "id": "DOC007",
        "title": "Procurement and Vendor Approval Process",
        "category": "Policy/Process",
        "text": (
            "Any purchase of goods or services must follow the procurement process. "
            "Requesters submit a purchase order describing the item, cost, and "
            "business justification. Finance reviews the budget while security "
            "reviews new software vendors for data protection risks. Contracts above "
            "ten thousand dollars require three competing quotes. Only approved "
            "vendors may be used, and all agreements are stored in the central "
            "contract repository for audit purposes."
        ),
    },
    # ================= SUPPORT / INCIDENTS (simulated tickets & reports) ======
    {
        "id": "DOC008",
        "title": "Incident Report: Login Service Outage",
        "category": "Support/Incidents",
        "text": (
            "At 09:15 users reported being unable to log in to the main web "
            "application. The on-call engineer confirmed the authentication service "
            "was returning errors because a certificate had expired. The team "
            "renewed the certificate and restarted the service, restoring access by "
            "10:02. Roughly four thousand users were affected during the outage. The "
            "root cause was a missing renewal alert. A follow-up action was created "
            "to automate certificate monitoring and prevent a repeat incident."
        ),
    },
    {
        "id": "DOC009",
        "title": "Incident Report: Database Latency Spike",
        "category": "Support/Incidents",
        "text": (
            "The database began responding slowly during peak traffic, causing page "
            "timeouts across the platform. Investigation showed a missing index on a "
            "large table combined with an inefficient query from a new feature. "
            "Engineers added the index and deployed a query fix, which reduced "
            "response times back to normal. The incident lasted about forty minutes. "
            "A postmortem recommended load testing new queries before release and "
            "improving database performance dashboards."
        ),
    },
    {
        "id": "DOC010",
        "title": "Support Ticket: Email Delivery Failure",
        "category": "Support/Incidents",
        "text": (
            "A customer reported that outgoing emails from their account were not "
            "being delivered. Support checked the mail server and found that the "
            "sending domain had been added to a spam blocklist after a configuration "
            "error. The team corrected the mail settings, requested delisting, and "
            "confirmed that new messages were delivered successfully. The ticket was "
            "closed after the customer verified that email was working again."
        ),
    },
    {
        "id": "DOC011",
        "title": "Support Ticket: VPN Disconnection Issues",
        "category": "Support/Incidents",
        "text": (
            "An employee working from home reported that the company VPN kept "
            "disconnecting every few minutes, interrupting access to internal tools. "
            "The help desk updated the VPN client to the latest version and adjusted "
            "the connection timeout settings. They also advised the user to switch "
            "to a wired connection where possible. After the changes the VPN "
            "remained stable and the ticket was resolved."
        ),
    },
    {
        "id": "DOC012",
        "title": "Support Ticket: Printer Not Responding",
        "category": "Support/Incidents",
        "text": (
            "A user in the finance department could not print invoices because the "
            "shared office printer showed as offline. The technician restarted the "
            "print spooler service and reinstalled the printer driver on the user's "
            "laptop. A paper jam was also cleared from the device. After these steps "
            "the printer came back online and test pages printed correctly, so the "
            "ticket was closed."
        ),
    },
    {
        "id": "DOC013",
        "title": "Support Ticket: Password Reset Request",
        "category": "Support/Incidents",
        "text": (
            "An employee was locked out of their account after too many failed login "
            "attempts. Following the security policy, the help desk verified the "
            "user's identity, reset the password, and required a change at next "
            "login. The agent also helped the user re-enroll in multi-factor "
            "authentication because their phone had been replaced. The user "
            "confirmed they could log in and the ticket was resolved."
        ),
    },
    {
        "id": "DOC014",
        "title": "Incident Report: API Returning 500 Errors",
        "category": "Support/Incidents",
        "text": (
            "External partners reported that the public API was returning server "
            "errors for several endpoints. The on-call team traced the problem to a "
            "failed deployment that left the service in an inconsistent state. They "
            "rolled back to the previous version, which stopped the errors within "
            "fifteen minutes. The incident affected integrations for about an hour. "
            "The postmortem added a smoke test to the deployment pipeline to catch "
            "similar failures earlier."
        ),
    },
    {
        "id": "DOC015",
        "title": "Support Ticket: Software Installation Access Denied",
        "category": "Support/Incidents",
        "text": (
            "A new employee could not install an approved design application because "
            "their account lacked administrator rights on the laptop. Support "
            "confirmed the software was on the approved list, pushed the "
            "installation through the device management system, and verified it "
            "launched correctly. The agent reminded the user that unapproved "
            "software must go through the procurement process before it can be "
            "installed."
        ),
    },
    # ================= FAQ (simulated help-center entries) ====================
    {
        "id": "DOC016",
        "title": "FAQ: Connecting to the Company VPN",
        "category": "FAQ",
        "text": (
            "How do I connect to the company VPN? Open the VPN client installed on "
            "your laptop, enter your work username and password, and approve the "
            "multi-factor prompt on your phone. If the connection drops frequently, "
            "update the client to the latest version or switch to a wired network. "
            "The VPN is required whenever you access internal systems from outside "
            "the office. Contact the help desk if you still cannot connect."
        ),
    },
    {
        "id": "DOC017",
        "title": "FAQ: How to Submit an Expense Claim",
        "category": "FAQ",
        "text": (
            "How do I get reimbursed for a business expense? Log in to the finance "
            "portal, create a new expense claim, attach a photo of each receipt, and "
            "select the correct category. Submit the claim within thirty days of the "
            "purchase. Your manager will review and approve it, and the money is paid "
            "in the next payroll cycle. Expenses over five hundred dollars need "
            "approval before you buy."
        ),
    },
    {
        "id": "DOC018",
        "title": "FAQ: Understanding Your Benefits",
        "category": "FAQ",
        "text": (
            "What benefits am I entitled to? Full-time employees receive health "
            "insurance, a retirement savings plan with company matching, and paid "
            "time off that grows with tenure. Open enrollment happens once a year, "
            "when you can change your health plan. Questions about coverage, "
            "dependents, or claims should go to the human resources team through the "
            "benefits portal."
        ),
    },
    {
        "id": "DOC019",
        "title": "FAQ: Installing Approved Software",
        "category": "FAQ",
        "text": (
            "Can I install software on my work laptop? You may install applications "
            "from the approved software catalog using the self-service portal, which "
            "does not require administrator rights. Software that is not on the list "
            "must first be reviewed through the procurement process for security and "
            "licensing. Never download tools from unknown websites, as this can "
            "introduce malware and policy violations."
        ),
    },
    {
        "id": "DOC020",
        "title": "FAQ: Recovering Account Access",
        "category": "FAQ",
        "text": (
            "I am locked out of my account, what should I do? If you entered the "
            "wrong password too many times, your account is temporarily locked for "
            "security. Wait fifteen minutes or contact the help desk to verify your "
            "identity and reset the password. You will be asked to set a new password "
            "and confirm multi-factor authentication. Keep your recovery phone number "
            "up to date to speed up this process."
        ),
    },
    {
        "id": "DOC021",
        "title": "FAQ: Booking a Meeting Room",
        "category": "FAQ",
        "text": (
            "How do I reserve a meeting room? Use the calendar system to find an "
            "available room, select the time slot, and add it to your meeting "
            "invitation. Rooms can be booked up to four weeks in advance. Please "
            "release rooms you no longer need so colleagues can use them. For large "
            "events, contact the facilities team to arrange additional seating and "
            "equipment."
        ),
    },
    # ================= MEETING MINUTES (simulated) ============================
    {
        "id": "DOC022",
        "title": "Meeting Minutes: Q3 Planning Session",
        "category": "Meeting Minutes",
        "text": (
            "The quarterly planning meeting reviewed goals for the next three "
            "months. The product team committed to shipping two major features, "
            "while engineering agreed to reduce technical debt and improve database "
            "performance after recent incidents. Marketing presented a campaign plan "
            "tied to the upcoming product launch. Budget owners confirmed spending "
            "targets. Action items were assigned with owners and due dates, and the "
            "group agreed to meet again in two weeks to track progress."
        ),
    },
    {
        "id": "DOC023",
        "title": "Meeting Minutes: Security Review",
        "category": "Meeting Minutes",
        "text": (
            "The security review meeting discussed recent risks and open findings. "
            "The team agreed to enforce multi-factor authentication for all remote "
            "access and to shorten the password rotation period. A recent phishing "
            "attempt was reviewed, and additional staff training was scheduled. The "
            "group also approved automating certificate monitoring following the "
            "login outage. Owners were assigned to each remediation item with a "
            "deadline before the next review."
        ),
    },
    {
        "id": "DOC024",
        "title": "Meeting Minutes: Product Roadmap Discussion",
        "category": "Meeting Minutes",
        "text": (
            "The roadmap meeting prioritized features for the next two releases. "
            "Customer feedback pointed to a need for better reporting and faster "
            "search. The team debated build versus buy for analytics and chose to "
            "prototype in-house first. Design agreed to deliver mockups within two "
            "weeks. Dependencies on the platform team were noted. The product manager "
            "will update the public roadmap and share it with stakeholders after the "
            "meeting."
        ),
    },
    {
        "id": "DOC025",
        "title": "Meeting Minutes: Hiring Sync",
        "category": "Meeting Minutes",
        "text": (
            "The hiring sync covered open roles across engineering and support. "
            "Recruiting reported a strong pipeline for the backend position and a "
            "shortage of qualified support candidates. The team agreed to refresh the "
            "job descriptions and speed up interview scheduling. Onboarding capacity "
            "was discussed to ensure new hires receive mentors. Hiring managers "
            "committed to giving interview feedback within two business days to avoid "
            "losing candidates."
        ),
    },
    {
        "id": "DOC026",
        "title": "Meeting Minutes: Budget Review",
        "category": "Meeting Minutes",
        "text": (
            "The budget review compared actual spending against the plan for the "
            "quarter. Travel costs were under budget because of increased remote "
            "work, while software subscriptions exceeded the forecast. Finance asked "
            "teams to consolidate overlapping tools and cancel unused licenses. The "
            "group approved additional budget for security improvements and database "
            "capacity. Updated forecasts will be circulated before the next planning "
            "session."
        ),
    },
    {
        "id": "DOC027",
        "title": "Meeting Minutes: Incident Postmortem Review",
        "category": "Meeting Minutes",
        "text": (
            "This postmortem meeting examined the recent API outage caused by a "
            "failed deployment. The timeline was reconstructed and the rollback was "
            "confirmed as the correct response. The group agreed that a smoke test in "
            "the deployment pipeline would have caught the problem. Action items "
            "included improving alerts, documenting the rollback steps, and running a "
            "game day to practice incident response. No individual was blamed; the "
            "focus was on process improvement."
        ),
    },
    # ================= NEWS / ARTICLES (public-style short articles) ==========
    {
        "id": "DOC028",
        "title": "Company Opens New Regional Office",
        "category": "News/Article",
        "text": (
            "The company announced the opening of a new regional office to support "
            "its growing customer base. The location will host sales, support, and "
            "engineering staff, creating around one hundred local jobs. Leadership "
            "said the office reflects strong demand and a commitment to being closer "
            "to customers. The site includes flexible workspaces designed for a mix "
            "of on-site and remote employees. Hiring for the new office begins next "
            "month."
        ),
    },
    {
        "id": "DOC029",
        "title": "New Product Launch Announced",
        "category": "News/Article",
        "text": (
            "The company unveiled its newest product at an industry event this week. "
            "The release focuses on faster analytics and an improved user interface "
            "based on customer feedback. Early access customers reported that the new "
            "reporting tools save them hours each week. The product will be available "
            "to all subscribers next quarter. Marketing plans a series of webinars to "
            "help users adopt the new features quickly."
        ),
    },
    {
        "id": "DOC030",
        "title": "Cybersecurity Trends to Watch This Year",
        "category": "News/Article",
        "text": (
            "Security experts highlight several trends shaping the year ahead. "
            "Phishing attacks are becoming more convincing, pushing organizations to "
            "adopt multi-factor authentication and stronger password practices. "
            "Companies are investing in employee training because people remain the "
            "most common point of failure. Experts also note the growing importance "
            "of monitoring and quick incident response to limit the damage from any "
            "breach that does occur."
        ),
    },
    {
        "id": "DOC031",
        "title": "The Rise of Remote and Hybrid Work",
        "category": "News/Article",
        "text": (
            "Remote and hybrid work arrangements have become a lasting part of the "
            "modern workplace. Studies suggest that flexible schedules can improve "
            "employee satisfaction and widen the hiring pool beyond a single city. "
            "At the same time, managers face new challenges in communication, fair "
            "evaluation, and keeping teams connected. Reliable tools such as secure "
            "VPN access and video conferencing are now considered essential rather "
            "than optional."
        ),
    },
    {
        "id": "DOC032",
        "title": "How Companies Are Adopting Artificial Intelligence",
        "category": "News/Article",
        "text": (
            "Businesses across industries are exploring how artificial intelligence "
            "can improve their operations. Common uses include automating repetitive "
            "tasks, summarizing documents, and helping employees find information "
            "faster. Analysts caution that successful adoption depends on clean data, "
            "clear goals, and training staff to work alongside the new tools. "
            "Organizations that treat AI as a support for human judgment, rather than "
            "a replacement, tend to see the best results."
        ),
    },
    {
        "id": "DOC033",
        "title": "Migrating Infrastructure to the Cloud",
        "category": "News/Article",
        "text": (
            "More organizations are moving their infrastructure to cloud platforms "
            "to gain flexibility and scale. A successful migration starts with an "
            "inventory of existing systems and a clear plan for data, security, and "
            "cost. Teams often move in phases, validating performance and backups at "
            "each step. Experts warn that lifting and shifting without optimization "
            "can raise costs, so reviewing architecture during the move is strongly "
            "recommended."
        ),
    },
]


def build_corpus(output_path: str = "corpus.csv") -> None:
    """Write all documents to a CSV file with columns id, title, text, category."""
    path = Path(output_path)
    fieldnames = ["id", "title", "text", "category"]

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for doc in DOCUMENTS:
            writer.writerow({key: doc[key] for key in fieldnames})

    # Small console summary so the run leaves visible evidence.
    categories: dict[str, int] = {}
    for doc in DOCUMENTS:
        categories[doc["category"]] = categories.get(doc["category"], 0) + 1

    print(f"Wrote {len(DOCUMENTS)} documents to {path.resolve()}")
    print("Documents per category:")
    for name, count in sorted(categories.items()):
        print(f"  {name:20s} {count}")


if __name__ == "__main__":
    build_corpus()

# 📘 Phase I — Planning, Requirement Analysis & OOAD (Weeks 1–3)

This phase focuses on project initiation, requirement analysis, functional modeling, and object-oriented design for the **Publications Summary Generator for Faculty Profile Building** system.  
The goal was to clearly define the problem scope, set up development infrastructure, and prepare UML design artifacts before implementation.

---

## 🗓️ Week 1 — Project Initiation & Problem Analysis

- Studied the manual faculty publication profile process and identified automation needs  
- Finalized project problem statement, scope, and expected outcomes  
- Prepared Project Vision and initial planning notes  
- Identified core domain entities: Faculty, Publication, Summary  
- Defined high-level system modules (user interaction, publication handling, summary generation)  
- Set up GitHub repository and project structure  
- Configured Jira board and sprint workflow  
- Created and organized initial product backlog  
- Sprint 1 started — status on track  

---

## 🗓️ Week 2 — Functional Modeling & Requirements Structuring

- Identified system actors (Faculty, Admin)  
- Derived primary and supporting use cases  
- Converted functional requirements into structured use cases  
- Prepared detailed Use Case descriptions (main & alternate flows)  
- Mapped use cases to Jira user stories for traceability  
- Defined system boundary and interaction flows  
- Validated requirements with sprint goals  
- Strengthened requirement coverage before design stage  

### 🧍 UML Use Case Diagram



## 🗓️ Week 3 — OOAD & UML Design Modeling

- Applied object-oriented analysis to domain model  
- Designed UML Class Diagram with OOPS principles  
- Used encapsulation and inheritance (User → Faculty/Admin)  
- Added service layer concepts (AI Service, Auth Service)  
- Created Sequence Diagram for AI paper evaluation flow  
- Created Activity Diagram for login → upload → report generation flow  
- Revised Class Diagram with AI Evaluation & Summary modules  
- Built UI prototype screens (Login, Dashboard, Upload, Results, Admin Panel)


## Week 4  – Dynamic Analysis
- Focus shifted from structural design to system behavior analysis.
- Identified system workflows and user interaction flow.
- Designed UML Activity Diagram to represent the end-to-end process of publication summary generation.
- Modeled major activities like faculty login, publication upload, input validation, NLP content extraction, summary generation, scoring, and database storage.
- Implemented decision nodes and parallel processing (fork/join) in the workflow.
- Defined dynamic use cases based on real user scenarios.
- Updated documentation and project repository with activity diagram and dynamic analysis notes.


## Week 5 - Interaction Modeling
- Focused on interaction modeling using UML Sequence Diagram.
- Analyzed object communication and message flow between system components.
- Modeled interactions between Faculty, Controller, NLP Module, Summary Generator, Score Calculator, and Database.
- Defined message passing and execution order during research paper upload and summary generation.
- Refined object responsibilities and system collaboration logic.
- Ensured alignment between sequence diagram and activity workflow created in the previous sprint.
- Updated documentation and repository with sequence diagram and interaction design artifacts.

## Week 6 - Detailed Class Design and System Packaging
- Project focused on detailed design phase using object-oriented design principles
- Class structure, relationships, interfaces, and modular packaging were defined
- System architecture refined for maintainability, modularity, and scalability
- Factory Pattern and Strategy Pattern adopted for flexible summary generation
- Key classes finalized: faculty data, publication management, summary generation, and data storage
- UML Class Diagram created with methods, visibility (+/–/#), inheritance, and interface implementation
- UML Package Diagram created to show dependencies and modular structure
- System organized into logical packages: models, services, controllers, NLP processing, and database layer
- OOP concepts applied — encapsulation, inheritance, and polymorphism
- Two summarization strategies planned: keyword-based and AI/NLP-based
- Git updated with UML diagrams, class design docs, and architecture folder
- Testing limited to design validation: class responsibility, interface usage, dependency analysis, and package cohesion

### 🧱 UML Class Diagram

> _(Add Class Diagram Image Here)_

### 🔄 UML Sequence Diagram

> _(Add Sequence Diagram Image Here)_

### ⚙️ UML Activity Diagram

> _(Add Activity Diagram Image Here)_

---

## 🛠️ Tools & Process Used

- GitHub — Version control & PR workflow  
- Jira — Sprint & backlog tracking  
- UML Modeling Tools — Diagram design  
- Agile Sprint Model — Phase execution  
- OOAD Principles — Domain-driven design  

---

## ✅ Phase I Outcome

- Clear problem definition and scope  
- Structured and traceable requirements  
- Actor & use case identification completed  
- Core UML diagrams prepared  
- OO domain model validated  
- Development and design base ready for implementation phase

---
 Validated domain model with requirements

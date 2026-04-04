# Product Requirements Document (PRD): phmedtecheu G-LMS
**Standardized Specifications for the Healthcare-Specialized German Learning Platform**

**Date**: April 4, 2026  
**Project Owner**: Christine Anne Gumboc (Client)  
**Lead Developer**: Aaron Christian Basa (Developer)

---

## 1. Project Vision
**phmedtecheu** is a high-fidelity Gamified Learning Management System (G-LMS) engineered for Filipino healthcare professionals transitioning to the European medical sector. The platform combines rigorous German language curriculum (A1–C1) with medical-specific career mapping and gamified engagement to ensure high certification success.

---

## 2. User Personas

### **A. The "Lehrling" (Student)**
*   **Profile**: Filipino nurse, medtech, or medical professional.
*   **Goal**: Pass B1/B2/C1 exams and secure a contract in Europe.
*   **Needs**: Mobile-first learning, clinical vocabulary, progress tracking, and community support.

### **B. The "Instruktor" (Admin/Client)**
*   **Profile**: Christine Anne Gumboc (Subject Matter Expert).
*   **Goal**: Manage courses, verify student progress, and provide premium consulting services.
*   **Needs**: A "Command Center" to upload lessons, track enrollments, and manage "Speaking Sessions" and "CV Letter" bookings.

---

## 3. Functional Requirements by Milestone

### **Phase 1: Foundation (COMPLETED)**
*   **Secure Auth**: Student & Admin login portals.
*   **Core LMS**: Multipage architecture for Courses, Lessons, and Categories.
*   **Admin Command Center**: Initial dashboard for content management.
*   **Sync Framework**: Local-to-Live server synchronization for regional stability.

### **Phase 2: Content & Service Engine (Milestone 2 - ₱40,000)**
*   **Advanced Resource Management**: Native support for Video (links/streaming), PDF/Documents, and Medical Vocabulary lists.
*   **Quiz Engine V1**: Interactive MCQ and "Fill-in-the-Blank" vocabulary quizzes based on the current `QuizQuestion` models.
*   **Additional Career Services**: Dedicated booking/request slots for:
    *   **CV & Motivation Letter Reviews**: Professional European-standard template generation.
    *   **European Readiness Checklist**: A custom digital tracker for documents (SRO, DFA, Apostille).
    *   **Deep Analysis Consultations**: One-on-one booking module for career mapping.
*   **Progress Tracking**: "Continue Learning" dashboard and lesson-level completion markers.

### **Phase 3: Gamification & Payment Integration (Milestone 3 - ₱40,000)**
*   **Online Payment Gateway**: Integration of automated student enrollment payments via **Stripe, PayPal, and GCash** (as per the Capacity Clause in the SAFS).
*   **UserProgression Engine**: Integration of XP (Experience Points) and Level-Up logic (Current `UserProgression` system).
*   **Career Milestones**: Level-based rewards (e.g., reaching Level 10 grants access to a clinical scenario workshop).
*   **Achievement Badges**: Automated rewards for "Perfect Quiz Scores," "7-Day Streaks," and "Level Completion."
*   **Visual Polish**: Medical-themed UI/UX enhancements and micro-animations for UX delight.

### **Phase 4: Launch & Verification (Milestone 4 - ₱40,000)**
*   **Full Data Seeding**: Migration of 12 complete health-specialized modules (A1–C1 content).
*   **Performance Hardening**: Caching, database optimization, and cross-border latency checks.
*   **User Acceptance Testing (UAT)**: Final 5-day verification period and "Live-Fire" launch.

---

## 4. Technical Stack
*   **Backend**: Python / Django (Modern, Scalable Monolith).
*   **Database**: SQLite (Development) / PostgreSQL (Production).
*   **Styling**: Vanilla CSS for premium, controlled aesthetics.
*   **Infrastructure**: Railway.app (European Server Hosting) & Namecheap (Domain Management).

---

## 5. Success Metrics
*   **Certification Readiness**: % of students passing mock exams within the app.
*   **Engagement**: Weekly active users (WAU) and average quiz scores.
*   **Revenue Performance**: Retention of students across multiple course levels (A1 to B2).

---

## 6. Project Roadmap (Tentative)
*   **April 2026**: Soft Launch / Milestone 2 & 3 Development.
*   **May 2026**: Phase 4 Seeding & UAT.
*   **June 2026**: Official **phmedtecheu** Public Launch.

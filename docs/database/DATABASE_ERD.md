# Database Entity Relationship Diagram

## Visual ERD

```mermaid
erDiagram
    USER ||--o{ CATEGORY : "has"
    USER ||--o{ SUBCATEGORY : "has"
    USER ||--o{ TRANSACTION : "creates"
    USER ||--o{ BUDGET_PERIOD : "owns"
    USER ||--o{ ACCOUNT : "has"
    USER ||--o{ RECURRING_INCOME_SOURCE : "has"
    USER ||--o{ RECURRING_BUDGET_ALLOCATION : "has"
    USER ||--o{ PASSWORD_RESET_TOKEN : "has"
    USER ||--o{ EMAIL_VERIFICATION : "has"
    
    CATEGORY ||--o{ SUBCATEGORY : "contains"
    
    SUBCATEGORY ||--o{ TRANSACTION : "categorizes"
    SUBCATEGORY ||--o{ BUDGET_ALLOCATION : "allocated_in"
    SUBCATEGORY ||--o{ RECURRING_BUDGET_ALLOCATION : "has"
    
    BUDGET_PERIOD ||--o{ BUDGET : "contains"
    
    BUDGET ||--o{ BUDGET_ALLOCATION : "has"
    BUDGET ||--o{ INCOME_SOURCE : "has"
    
    INCOME_SOURCE }o--|| RECURRING_INCOME_SOURCE : "derived_from"
    BUDGET_ALLOCATION }o--o| RECURRING_BUDGET_ALLOCATION : "derived_from"

    USER {
        int id PK
        string username UK "unique, not null"
        string email UK "unique, not null"
        string password_hash "not null"
        string first_name "not null"
        string last_name "not null"
        string display_name "nullable"
        string currency "default: USD"
        string theme "default: dark"
        datetime created_at
        string country "nullable"
        string preferred_name "nullable"
        string referral_source "nullable"
        text referral_details "nullable"
        boolean email_verified "default: false"
    }

    CATEGORY {
        int id PK
        string name "not null"
        int user_id FK "references USER.id"
        boolean is_template "default: false"
        datetime created_at
    }

    SUBCATEGORY {
        int id PK
        string name "not null"
        int category_id FK "references CATEGORY.id"
        datetime created_at
        unique name_category "name + category_id"
    }

    TRANSACTION {
        int id PK
        float amount "not null"
        string description
        text comment
        int subcategory_id FK "references SUBCATEGORY.id, not null"
        int user_id FK "references USER.id, not null"
        datetime transaction_date
    }

    BUDGET_PERIOD {
        int id PK
        string name "not null"
        string period_type "not null (monthly/quarterly/yearly/custom)"
        date start_date "not null"
        date end_date "not null"
        int user_id FK "references USER.id, not null"
        boolean is_active "default: false"
        datetime created_at
    }

    BUDGET {
        int id PK
        int period_id FK "references BUDGET_PERIOD.id, not null"
        float total_income "default: 0"
        float balance_brought_forward "default: 0"
        int user_id FK "references USER.id, not null"
        datetime created_at
    }

    BUDGET_ALLOCATION {
        int id PK
        float allocated_amount "default: 0"
        int subcategory_id FK "references SUBCATEGORY.id, not null"
        int budget_id FK "references BUDGET.id, not null"
        boolean is_recurring_allocation "default: false"
        int recurring_allocation_id FK "references RECURRING_BUDGET_ALLOCATION.id, nullable"
    }

    INCOME_SOURCE {
        int id PK
        string name "not null"
        float amount "not null"
        int budget_id FK "references BUDGET.id, not null"
        boolean is_recurring_source "default: false"
        int recurring_source_id FK "references RECURRING_INCOME_SOURCE.id, nullable"
        datetime created_at
    }

    RECURRING_INCOME_SOURCE {
        int id PK
        string name "not null"
        float amount "not null"
        int user_id FK "references USER.id, not null"
        boolean is_active "default: true"
        datetime created_at
        datetime updated_at
    }

    RECURRING_BUDGET_ALLOCATION {
        int id PK
        float allocated_amount "default: 0"
        int subcategory_id FK "references SUBCATEGORY.id, not null"
        int user_id FK "references USER.id, not null"
        boolean is_active "default: true"
        datetime created_at
        datetime updated_at
    }

    ACCOUNT {
        int id PK
        string name "not null"
        string account_type "not null (checking/savings/credit/investment/cash/other)"
        string bank_name
        string account_number
        float current_balance "default: 0"
        int user_id FK "references USER.id, not null"
        datetime created_at
        datetime updated_at
        boolean is_active "default: true"
    }

    PASSWORD_RESET_TOKEN {
        int id PK
        int user_id FK "references USER.id, not null"
        string token UK "unique, not null"
        datetime expires_at "not null"
        boolean used "default: false"
    }

    EMAIL_VERIFICATION {
        int id PK
        int user_id FK "references USER.id, not null"
        string token UK "unique, not null"
        datetime expires_at "not null"
        boolean verified "default: false"
        datetime created_at
    }
```

## Entity Descriptions

### Core Entities

#### USER
The central entity representing application users. Stores authentication credentials, profile information, and preferences.

#### CATEGORY
Top-level categorization of transactions. Each category belongs to a user and can contain multiple subcategories.

#### SUBCATEGORY
Detailed categorization within categories. Has a unique constraint on `(name, category_id)` to prevent duplicates within the same category.

#### TRANSACTION
Financial transactions (expenses) recorded by users. Amounts are stored as negative values for expenses. Linked to both user and subcategory.

### Budget Management Entities

#### BUDGET_PERIOD
Time-based organization for budgets (e.g., "January 2024", "Q1 2024"). Only one period can be active per user at a time.

#### BUDGET
Financial plan associated with a budget period. Tracks total income and balance brought forward.

#### BUDGET_ALLOCATION
Links budget amounts to specific subcategories. Can be marked as recurring if derived from a recurring allocation template.

#### INCOME_SOURCE
Income entries for a specific budget. Can be linked to a recurring income source template.

### Recurring Templates

#### RECURRING_INCOME_SOURCE
Template for recurring income that can be automatically applied to new budgets.

#### RECURRING_BUDGET_ALLOCATION
Template for recurring budget allocations that can be automatically applied to new budgets.

### Account Management

#### ACCOUNT
Financial accounts (checking, savings, credit cards, etc.) owned by users. Supports soft deletion via `is_active` flag.

### Authentication

#### PASSWORD_RESET_TOKEN
Temporary tokens for secure password reset functionality.

#### EMAIL_VERIFICATION
Tokens for email verification during registration.

## Relationship Summary

- **USER** has one-to-many relationships with all other entities
- **CATEGORY** to **SUBCATEGORY**: One-to-many (cascade delete)
- **SUBCATEGORY** to **TRANSACTION**: One-to-many
- **SUBCATEGORY** to **BUDGET_ALLOCATION**: One-to-many
- **BUDGET_PERIOD** to **BUDGET**: One-to-many (one budget per period)
- **BUDGET** to **BUDGET_ALLOCATION**: One-to-many
- **BUDGET** to **INCOME_SOURCE**: One-to-many
- **RECURRING_INCOME_SOURCE** to **INCOME_SOURCE**: One-to-many (optional)
- **RECURRING_BUDGET_ALLOCATION** to **BUDGET_ALLOCATION**: One-to-many (optional)

## Key Constraints

1. **Unique Username & Email**: Each user must have a unique username and email
2. **Unique Subcategory Name per Category**: Cannot have duplicate subcategory names within the same category
3. **Single Active Period**: Only one budget period can be active per user at a time
4. **Cascade Deletes**: 
   - Deleting a user deletes all related data
   - Deleting a category deletes its subcategories
   - Deleting a budget period deletes its budgets
   - Deleting a budget deletes its allocations and income sources

## Notes

- Transaction amounts are stored as **negative values** for expenses
- The `is_active` flag on accounts and recurring items allows for soft deletion
- Budget allocations can be marked as recurring if they come from recurring templates
- The unique constraint on subcategories prevents duplicate names within categories


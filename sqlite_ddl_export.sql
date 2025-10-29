-- Table: account
CREATE TABLE account (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	account_type VARCHAR(50) NOT NULL, 
	bank_name VARCHAR(100), 
	account_number VARCHAR(50), 
	current_balance FLOAT, 
	user_id INTEGER NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	is_active BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
)
;

-- Table: budget
CREATE TABLE budget (
	id INTEGER NOT NULL, 
	period_id INTEGER NOT NULL, 
	total_income FLOAT, 
	balance_brought_forward FLOAT, 
	user_id INTEGER NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(period_id) REFERENCES budget_period (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
)
;

-- Table: budget_allocation
CREATE TABLE "budget_allocation" (
	id INTEGER NOT NULL, 
	allocated_amount FLOAT, 
	subcategory_id INTEGER NOT NULL, 
	budget_id INTEGER NOT NULL, 
	is_recurring_allocation BOOLEAN, 
	recurring_allocation_id INTEGER, 
	PRIMARY KEY (id), 
	CONSTRAINT fk_budget_allocation_recurring FOREIGN KEY(recurring_allocation_id) REFERENCES recurring_budget_allocation (id), 
	FOREIGN KEY(budget_id) REFERENCES budget (id), 
	FOREIGN KEY(subcategory_id) REFERENCES subcategory (id)
)
;

-- Table: budget_period
CREATE TABLE budget_period (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	period_type VARCHAR(20) NOT NULL, 
	start_date DATE NOT NULL, 
	end_date DATE NOT NULL, 
	user_id INTEGER NOT NULL, 
	is_active BOOLEAN, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
)
;

-- Table: category
CREATE TABLE category (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	user_id INTEGER NOT NULL, 
	is_template BOOLEAN, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
)
;

-- Table: email_verification
CREATE TABLE email_verification (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	token VARCHAR(100) NOT NULL, 
	expires_at DATETIME NOT NULL, 
	verified BOOLEAN, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id), 
	UNIQUE (token)
)
;

-- Table: income_source
CREATE TABLE "income_source" (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	amount FLOAT NOT NULL, 
	budget_id INTEGER NOT NULL, 
	created_at DATETIME, 
	is_recurring_source BOOLEAN, 
	recurring_source_id INTEGER, 
	PRIMARY KEY (id), 
	CONSTRAINT fk_income_source_recurring FOREIGN KEY(recurring_source_id) REFERENCES recurring_income_source (id), 
	FOREIGN KEY(budget_id) REFERENCES budget (id)
)
;

-- Table: password_reset_token
CREATE TABLE password_reset_token (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	token VARCHAR(100) NOT NULL, 
	expires_at DATETIME NOT NULL, 
	used BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id), 
	UNIQUE (token)
)
;

-- Table: recurring_budget_allocation
CREATE TABLE recurring_budget_allocation (
	id INTEGER NOT NULL, 
	allocated_amount FLOAT, 
	subcategory_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	is_active BOOLEAN, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(subcategory_id) REFERENCES subcategory (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
)
;

-- Table: recurring_income_source
CREATE TABLE recurring_income_source (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	amount FLOAT NOT NULL, 
	user_id INTEGER NOT NULL, 
	is_active BOOLEAN, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
)
;

-- Table: subcategory
CREATE TABLE "subcategory" (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	category_id INTEGER NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_subcategory_name_category UNIQUE (name, category_id), 
	FOREIGN KEY(category_id) REFERENCES category (id)
)
;

-- Table: transaction
CREATE TABLE "transaction" (
	id INTEGER NOT NULL, 
	amount FLOAT NOT NULL, 
	description VARCHAR(200), 
	comment TEXT, 
	subcategory_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	transaction_date DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(subcategory_id) REFERENCES subcategory (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
)
;

-- Table: user
CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR(80) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(120) NOT NULL, 
	first_name VARCHAR(50) NOT NULL, 
	last_name VARCHAR(50) NOT NULL, 
	display_name VARCHAR(100), 
	currency VARCHAR(10), 
	theme VARCHAR(10), 
	created_at DATETIME, 
	country VARCHAR(100), 
	preferred_name VARCHAR(100), 
	referral_source VARCHAR(100), 
	referral_details TEXT, 
	email_verified BOOLEAN, 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email)
)
;

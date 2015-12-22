DROP TABLE JOB;
DROP TABLE USER;

CREATE TABLE USER(
        user_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
        user_name VARCHAR(30) NOT NULL UNIQUE,
        password CHAR(66) NOT NULL,
        exist_job_limit INT DEFAULT 5,
        running_job_limit INT DEFAULT 3,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        history_job_num INT DEFAULT 0,
        history_success_job_num INT DEFAULT  0);

CREATE TABLE JOB(
 job_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
     job_name VARCHAR(30) NOT NULL,
     user_id INT NOT NULL,
     job_type VARCHAR(20) NOT NULL,
     job_conf VARCHAR(50) NOT NULL,
     job_status VARCHAR(10) NOT NULL,
     log_file VARCHAR(50) NOT NULL,
     log_deleted BOOLEAN DEFAULT 0,
     active BOOLEAN DEFAULT 1,
     create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
     end_time DATETIME,
     running_pid INT,
     FOREIGN KEY (user_id) REFERENCES USER(user_id));

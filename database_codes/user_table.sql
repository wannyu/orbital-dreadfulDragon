CREATE TABLE user (
    userID BIGINT PRIMARY KEY,
    household INT NOT NULL,
    points BIGINT NOT NULL,
    startDate DATE NOT NULL,
    weeklyServings INT NOT NULL,
    servingLimit INT NOT NULL,
    username VARCHAR(1000) NOT NULL, 
    reminderFreq INT NOT NULL
);
 

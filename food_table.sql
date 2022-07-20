CREATE TABLE food (
    foodID INT PRIMARY KEY,
    foodName VARCHAR (1000) NOT NULL,
    servings INT NOT NULL,
    expiryDate DATE NOT NULL,
    userID BIGINT NOT NULL,
    FOREIGN KEY (userID) REFERENCES users(userID)
);

-- 用户信息
DROP TABLE IF EXISTS UsersLogin;
DROP TABLE IF EXISTS UsersInfo;
DROP TABLE IF EXISTS HotQAs;
DROP TABLE IF EXISTS Doctors;
DROP TABLE IF EXISTS ExportedSessions;
DROP TABLE IF EXISTS GoingSessions;

CREATE TABLE UsersLogin(username TEXT, password TEXT);
CREATE TABLE UsersInfo(username TEXT, sex INT, birthday TEXT, region TEXT, phone TEXT, info TEXT, avatar TEXT);
CREATE TABLE HotQAs(qaid INT, question TEXT, answer TEXT);
CREATE TABLE Doctors(uername TEXT, real_name TEXT, career_year INT, hospital TEXT, post TEXT, good_at TEXT, wechat TEXT);
CREATE TABLE ExportedSessions(username TEXT, session_id TEXT, session_json TEXT);
CREATE TABLE GoingSessions(username TEXT, session_id TEXT, session_json TEXT);
CREATE TABLE PublicSessions(username TEXT, session_id TEXT, session_json TEXT);



-- 用户信息
INSERT INTO UsersLogin(0, username , password) VALUES ("fanvane", "123456");
INSERT INTO UsersInfo(0, "恐怖猫猫", 0, 18, "黑龙江省哈尔滨市", "12365485962");
INSERT INTO HotQAs("我是谁？", "比比鸟！");
INSERT INTO Doctors(0, "华佗", "外科手术专家。")





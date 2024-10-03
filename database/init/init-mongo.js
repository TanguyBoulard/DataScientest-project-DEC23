db = db.getSiblingDB("admin");
db.createUser({
  user: process.env.MONGO_USER,
  pwd: process.env.MONGO_PASSWORD,
  roles: [ { role: "readWrite", db: process.env.MONGO_INITDB_DATABASE } ]
});

db = db.getSiblingDB(process.env.MONGO_INITDB_DATABASE);
db.createCollection("city");
db.createCollection("weather");
db.createCollection("daily_weather");
db.createCollection("air_pollution");
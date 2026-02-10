export const config = {
  port: parseInt(process.env.PORT || "4000"),
  dbPath: process.env.DB_PATH || "/app/data/ccobs.db",
  corsOrigins: process.env.CORS_ORIGINS || "*",
};

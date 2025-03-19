using Microsoft.Extensions.Options;
using Scoring.Utils;
using System.Data.SqlClient;

namespace Scoring.Repository
{
    public class Connector
    {
        private readonly SqlConnection connection;
        private readonly string _connectionString;
        private readonly ILogger<Connector> _logger;

        public Connector(IOptions<AppSettings> appSettings, ILogger<Connector> logger)
        {
            _connectionString = appSettings.Value.MyDatabaseConnection;
            _logger = logger;

            try
            {
                connection = new SqlConnection(_connectionString);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при подключении к БД: {ConnStr}", _connectionString);
            }
        }

        public List<object[]> ExecuteSelect(string cmdTxt, Dictionary<string, object> parameters = null)
        {
            List<object[]> result = new List<object[]>();

            try
            {
                using (var command = new SqlCommand(cmdTxt, connection))
                {
                    if (parameters != null)
                    {
                        foreach (var parameter in parameters)
                        {
                            command.Parameters.AddWithValue("@" + parameter.Key, parameter.Value);
                        }
                    }

                    connection.Open();

                    using (var reader = command.ExecuteReader())
                    {
                        int columnCount = reader.FieldCount;

                        while (reader.Read())
                        {
                            object[] row = new object[columnCount];
                            reader.GetValues(row);
                            result.Add(row);
                        }
                    }
                }
            }
            catch (SqlException ex)
            {
                _logger.LogError(ex, "Ошибка при подключении к БД: {ConnStr}", ex.Message);
            }
            finally
            {
                connection.Close();
            }

            return result;
        }
    }
}

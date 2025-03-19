using Microsoft.AspNetCore.Mvc;
using Scoring.DTO;
using Scoring.Models;
using System.Diagnostics;

namespace PaperKiller.Controllers
{
    public class HomeController : Controller
    {
        private readonly ILogger<HomeController> _logger;

        public HomeController(ILogger<HomeController> logger)
        {
            _logger = logger;
        }

        public ActionResult<ErrorResponseDTO> Index()
        {
            return View();
        }

        public ActionResult<ErrorResponseDTO> Privacy()
        {
            return View();
        }

        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public ActionResult<ErrorResponseDTO> Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}
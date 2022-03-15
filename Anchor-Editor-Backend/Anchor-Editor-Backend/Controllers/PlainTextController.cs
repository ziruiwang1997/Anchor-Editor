using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Text.RegularExpressions;

namespace Anchor_Editor_Backend.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class PlainTextController : ControllerBase
    {
        public PlainTextController()
        {

        }

        [HttpGet]
        public IActionResult GetPlainTextAsString()
        {
            string plainText = "DEFAULT STRING";
            return Ok(plainText);
        }
    }
}

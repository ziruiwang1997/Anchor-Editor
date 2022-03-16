using Anchor_Editor_Backend.Models;
using System.Collections.Generic;

namespace Anchor_Editor_Backend.Repository
{
    public interface IAnchorRepository
    {
        IList<Anchor> AnchorList { get; set; }

        public Anchor GetAnchorByTimestamp(string timestamp);

        public IList<Anchor> GetAnchorByLocation(int location);

        public void DeleteAnchorByTimestamp(string timestamp);

        public void AddAnchorByTimestamp(string timestamp, int location);

        public void EditAnchor(string originalTimestamp, int originalLocation, string destinationTimestamp, int destinationLocation);
    }
}

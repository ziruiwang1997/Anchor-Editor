using Anchor_Editor_Backend.Models;
using System.Collections.Generic;
using System.Linq;

namespace Anchor_Editor_Backend.Repository
{
    public class AnchorRepository : IAnchorRepository
    {
        public IList<Anchor> AnchorList { get; set; }

        public Anchor GetAnchorByTimestamp(string timestamp)
        {
            Anchor anchor = AnchorList.Where(x => x.Timestamp == timestamp).FirstOrDefault();
            return anchor;
        }

        public IList<Anchor> GetAnchorByLocation(int location)
        {
            IList<Anchor> anchor = AnchorList.Where(x => x.Location == location).ToList();
            return anchor;
        }

        public void DeleteAnchorByTimestamp(string timestamp)
        {
            var anchorsToRemove = AnchorList.Where(x => x.Timestamp == timestamp).ToList();
            foreach (var anchor in anchorsToRemove)
                AnchorList.Remove(anchor);
        }

        public void AddAnchorByTimestamp(string timestamp, int location)
        {
            Anchor anchor = new Anchor(timestamp, location);    
            AnchorList.Add(anchor);
        }

        public void EditAnchor(string originalTimestamp, int originalLocation, string destinationTimestamp, int destinationLocation)
        {
            Anchor anchor = AnchorList.Where(x => x.Timestamp == originalTimestamp && x.Location == originalLocation).FirstOrDefault();
            anchor.Timestamp = destinationTimestamp;
            anchor.Location = destinationLocation;
        }
    }
}

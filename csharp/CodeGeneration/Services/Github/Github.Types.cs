namespace CodeGeneration.Services.GitHub {

    /// <summary>
    /// GitHub issue interface
    /// </summary>
    internal class Issue
    {
        public int id { get; set; }
        public int number { get; set; }
        public string? title { get; set; }
        public string? body { get; set; }
    }

    /// <summary>
    /// GitHub API parameter interface
    /// </summary>
    internal class Parameter {    
        public string Label {get; set;} = "";
        public string State {get; set;} = "";
    }

}
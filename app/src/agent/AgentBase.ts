export abstract class AgentBase {
  protected agentName: string;

  constructor(agentName: string) {
    this.agentName = agentName;
  }

  public getAgentName(): string {
    return this.agentName;
  }

  protected log(message: string, data?: any) {
    console.log(`[Agent: ${this.agentName}] ${message}`, data || "");
  }
}

# Imports

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optims
import torch.distributions as distribs





# Log

def log(text):
    print("[" + time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()) + "] " + text)
    
    
    
    
# Discrete action

class Model(nn.Module):
    def __init__(self, state_size, action_size):
        super(Model, self).__init__()
        
        self.actor_network = nn.Sequential(
            nn.Linear(state_size, 512),
            nn.SELU(),
            nn.Linear(512, 256),
            nn.SELU(),
            nn.Linear(256, 128),
            nn.SELU(),
            nn.Linear(128, action_size)
        )
        
        self.critic_network = nn.Sequential(
            nn.Linear(state_size, 512),
            nn.SELU(),
            nn.Linear(512, 256),
            nn.SELU(),
            nn.Linear(256, 128),
            nn.SELU(),
            nn.Linear(128, 1)
        )
        
        
    def act(self, state):
        action_probs = F.softmax(self.actor_network(state), -1)
        action_distrib = distribs.Categorical(action_probs)
        
        return action_distrib
    
    
    def evaluate(self, state):
        return self.critic_network(state)
        
        
        
        
        
# Continuous action, std parameter

class Model(nn.Module):
    def __init__(self, state_size, action_size):
        super(Model, self).__init__()
        
        self.actor_network = nn.Sequential(
            nn.Linear(state_size, 512),
            nn.SELU(),
            nn.Linear(512, 256),
            nn.SELU(),
            nn.Linear(256, 128),
            nn.SELU()
        )
        
        self.critic_network = nn.Sequential(
            nn.Linear(state_size, 512),
            nn.SELU(),
            nn.Linear(512, 256),
            nn.SELU(),
            nn.Linear(256, 128),
            nn.SELU(),
            nn.Linear(128, 1)
        )
        
        
        self.action_mean_layer = nn.Linear(128, 1)
        self.action_std_param = nn.Parameter(torch.zeros(1, action_size))
        
        
    def act(self, state):
        action_mean = self.action_mean_layer(hidden_output)
        action_std = self.action_std_param.exp().expand_as(action_mean)
        
        action_distrib = distribs.Normal(action_mean, action_std)
        
        return action_distrib
    
    
    def evaluate(self, state):
        return self.critic_network(state)
        
        
        
        
        
        
# Continuous action, std layer

class Model(nn.Module):
    def __init__(self, state_size, action_size):
        super(Model, self).__init__()
        
        self.actor_network = nn.Sequential(
            nn.Linear(state_size, 512),
            nn.SELU(),
            nn.Linear(512, 256),
            nn.SELU(),
            nn.Linear(256, 128),
            nn.SELU()
        )
        
        self.critic_network = nn.Sequential(
            nn.Linear(state_size, 512),
            nn.SELU(),
            nn.Linear(512, 256),
            nn.SELU(),
            nn.Linear(256, 128),
            nn.SELU(),
            nn.Linear(128, 1)
        )
        
        
        self.action_mean_layer = nn.Linear(128, 1)
        self.action_std_layer = nn.Linear(128, 1)
        
        
    def act(self, state):
        action_mean = self.amount_mean_layer(hidden_output)
        action_std = F.relu(self.amount_std_layer(hidden_output))
        
        action_distrib = distribs.Normal(action_mean, action_std)
        
        return action_distrib
    
    
    def evaluate(self, state):
        return self.critic_network(state)
        
        
        
        

# Initializing layer weight and bias

self.layer.weight.data.mul_(0.1)
self.layer.bias.data.mul_(0.0)





# Load model

model = torch.load("model.pkl")




# Save model

torch.save(model, "model.pkl")





# Create optimizer

optim = optims.Adam(model.parameters())





# Compute returns
def compute_returns(memory, next_value, gamma=0.99):
    memory.returns = torch.zeros((len(memory.rewards), 1))
    
    R = next_value
    
    for i in reversed(range(len(memory.rewards))):
        R = memory.rewards[i] + gamma * R
        
        memory.returns[i] = R
        
        
        
        
        
# Compute simple advantages
def compute_advantages(memory):
    advantages = memory.returns - memory.values
    



# Compute Generalized Advantage Estimation
def compute_gae(memory, next_value, gamma=0.99, lambda_=0.95):
    memory.advantages = torch.zeros((len(memory.rewards), 1))
    
    gae = 0.0
    
    for i in reversed(range(len(memory.rewards))):
        delta = memory.rewards[i] + gamma * next_value - memory.values[i]
        
        gae = delta + (gamma * lambda_) * gae
        
        memory.advantages[i] = gae
        
        next_value = memory.values[i]





# Normalize advantages
def normalize_advantages(memory, eps=1e-8):
    memory.advantages -= memory.advantages.mean()
    memory.advantages /= (memory.advantages.std() + eps)
    
    
    
    
    
# Compute entropy
entropy = action_distrib.entropy()





# Compute simple actor loss
actor_loss = -(log_probs * minibatch_memory.advantages).mean()


# Compute PPO actor loss
unclipped_ratio = (log_probs - minibatch_memory.log_probs).exp()
clipped_ratio = torch.clamp(unclipped_ratio, 1.0 - CLIP_PARAM, 1.0 + CLIP_PARAM)

unclipped_actor_loss = unclipped_ratio * minibatch_memory.advantages
clipped_actor_loss = clipped_ratio * minibatch_memory.advantages

actor_loss = -torch.min(unclipped_actor_loss, clipped_actor_loss).mean()





# Calculate advantage critic loss
critic_loss = advantages.pow(2).mean() * 0.5


# Calculate MSE critic loss
critic_loss = VALUE_COEF * mse_loss(values, minibatch_memory.returns) * 0.5


# Calculate clipped critic loss
clipped_values = minibatch_memory.values + torch.clamp(values - minibatch_memory.values, -CLIP_PARAM, CLIP_PARAM)

unclipped_critic_loss = values - returns
clipped_critic_loss = clipped_values - returns

critic_loss = VALUE_COEF * torch.max(critic_unclipped, critic_clipped).pow(2).mean() * 0.5





# Calculate entropy loss
entropy_loss = -entropies.mean() * 0.001




# Calculate final loss
loss = actor_loss + critic_loss + entropy_loss






# Simple update
optim.zero_grad()

loss.backward()

optim.step()



# Update with gradient norm clip
optim.zero_grad()

loss.backward()

torch.nn.utils.clip_grad_norm_(model.parameters(), MAX_GRAD_NORM)

optim.step()
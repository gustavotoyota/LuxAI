import os




import torch
import torch.nn.functional as F

import torch.utils.data
import torch.utils.data.dataloader

import adabelief_pytorch




import lux_datasets
import lux_model




import hdf5plugin





if __name__ == '__main__':
  map_size = 12




  # Get model

  model_dir_path = f'models'
  model_file_path = f'{model_dir_path}/model_{map_size}.pt'

  if os.path.isfile(model_file_path):
    model = torch.load(model_file_path)
  else:
    model = lux_model.LuxModel(map_size, map_size)




  # Create optimizer

  optimizer = adabelief_pytorch.AdaBelief(
    model.parameters(),
    lr=1e-3,
    #weight_decay=1e-5,
    print_change_log=False
  )




  # Data loader

  singleSamplingDataset = lux_datasets.HDF5SingleSamplingDataset(f'samples/{map_size}.h5')
  batchSamplingDataset = lux_datasets.HDF5BatchDataset(f'samples/{map_size}.h5')

  dataloader = torch.utils.data.dataloader.DataLoader(
    dataset=singleSamplingDataset,
    batch_size=256,
    shuffle=True,

    # dataset=batchSamplingDataset,
    # sampler=torch.utils.data.dataloader.BatchSampler(
    #   sampler=torch.utils.data.dataloader.RandomSampler(batchSamplingDataset),
    #   batch_size=128,
    #   drop_last=True,
    # ),

    pin_memory=True,
    # num_workers=2,
  )




  # CUDA

  if torch.cuda.is_available():
    model = model.cuda()




  while True:
    for minibatch in dataloader:
      observation = torch.Tensor(minibatch[0]).cuda().squeeze(0)
      policy_target = torch.Tensor(minibatch[1]).cuda().squeeze(0)
      value_target = torch.Tensor(minibatch[2]).cuda().squeeze(0)

      action_probs, values = model(observation, False)
      
      policy_loss = F.binary_cross_entropy_with_logits(action_probs, policy_target)
      value_loss = F.mse_loss(values, value_target)

      loss = policy_loss + value_loss
      print('Loss:', loss.item())

      optimizer.zero_grad()
      loss.backward()
      optimizer.step()



    os.makedirs(model_dir_path, exist_ok=True)
    torch.save(model, model_file_path)


    
    print('Finished batch')